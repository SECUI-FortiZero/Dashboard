from __future__ import annotations

import ansible_runner
import os
import tempfile
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from app.connector_db import get_connection

load_dotenv()


# ==============================
# On-prem 정책 적용 (Ansible)
# ==============================
def apply_rules(rules, default_policy=None, policy_name="unnamed"):
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    playbook_path = os.path.join(project_root, 'ansible', 'playbook_apply.yml')

    host = os.getenv('ONPREM_HOST', '192.168.5.10')
    user = os.getenv('ONPREM_USER', 'linux')
    key  = os.getenv('ONPREM_SSH_KEY_PATH', '/home/soobin/.ssh/id_rsa')
    port = os.getenv('ONPREM_PORT', '22')

    # (선택) 관리 CIDR 고정 허용을 Ansible로 넘기고 싶다면 .env에 MGMT_ALLOW_CIDRS=cidr1,cidr2 설정
    mgmt_allow = [x.strip() for x in os.getenv("MGMT_ALLOW_CIDRS", "").split(",") if x.strip()]

    with tempfile.TemporaryDirectory() as tmpdir:
        # 디버그: runner가 실제 쓰는 인벤토리 내용 확인
        inventory_content = f"""
[firewall_servers]
{host} ansible_user={user} ansible_port={port} ansible_ssh_private_key_file={key}
"""
        print("=== INVENTORY ===")
        print(inventory_content)

        inventory_path = os.path.join(tmpdir, 'inventory.ini')
        with open(inventory_path, 'w') as f:
            f.write(inventory_content)

        extravars = {
            'rules_from_api': rules,
            'default_policy': default_policy or {},
            'policy_name': policy_name,
            'ansible_become': True,
            'ansible_become_method': 'sudo',
            'ansible_become_password': os.getenv('ONPREM_BECOME_PASS', ''),
            # 선택: 관리 CIDR 화이트리스트(플레이북에서 사용 가능)
            'mgmt_allow_cidrs': mgmt_allow,
        }
        print("=== EXTRAVARS ===")
        print(extravars)

        r = ansible_runner.run(
            private_data_dir=tmpdir,
            playbook=playbook_path,
            inventory=inventory_path,
            extravars=extravars
        )

        if r.rc != 0:
            # stdout 파일 경로 구성 (runner ident 기준)
            ident = getattr(r, 'ident', None) or 'unknown'
            stdout_path = os.path.join(tmpdir, 'artifacts', ident, 'stdout')
            err_txt = ""
            try:
                with open(stdout_path, 'r', encoding='utf-8', errors='ignore') as f:
                    err_txt = f.read()
            except Exception:
                # stdout 못 읽으면 status라도 반환
                err_txt = str(getattr(r, 'status', 'failed'))

            raise Exception(f"Ansible playbook failed (rc={r.rc}): {err_txt}")

        # 요약 반환
        summary = getattr(r, 'stats', {})
        return {"status": "success", "rc": r.rc, "summary": summary}


# ==============================
# DB 스냅샷 기반: 현재(on-prem) 규칙 조회
# ==============================

def _get_latest_onprem_version(policy_name: Optional[str] = None) -> Optional[int]:
    """
    policies/policy_versions에서 '가장 최신 버전'의 version_id 반환.
    policy_name 주면 해당 정책 이름으로 한정.
    """
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        if policy_name:
            cur.execute(
                """
                SELECT pv.id AS version_id
                FROM policy_versions pv
                JOIN policies p ON p.id = pv.policy_id
                WHERE p.name = %s
                ORDER BY pv.created_at DESC, pv.id DESC
                LIMIT 1
                """,
                (policy_name,),
            )
        else:
            cur.execute(
                """
                SELECT pv.id AS version_id
                FROM policy_versions pv
                ORDER BY pv.created_at DESC, pv.id DESC
                LIMIT 1
                """
            )
        row = cur.fetchone()
        return row["version_id"] if row else None
    finally:
        cur.close()
        conn.close()


def _map_rule_to_dashboard_format(r: Dict[str, Any]) -> Dict[str, Any]:
    """
    policy_rules 한 행을 /policy/current에서 쓰는 on-prem 포맷으로 변환.
    """
    port_val = r.get("dport")

    # 단일 숫자 문자열이면 int로, 범위/복합은 문자열 유지
    if isinstance(port_val, str) and port_val.isdigit():
        port_out: Any = int(port_val)
    else:
        port_out = port_val  # None/문자열/이미 숫자

    out = {
        "platform": "on-premise",
        "chain": r.get("chain"),
        "protocol": r.get("proto"),
        "source_ip": r.get("src"),
        "destination_ip": r.get("dst"),
        "port": port_out,
        "action": r.get("target"),
        "comment": r.get("comment"),
    }
    if r.get("state"):
        out["state"] = r["state"]
    return out


def fetch_rules(policy_name: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    /api/policy/current 에서 사용.
    - DB 스냅샷 기반: 최신 policy_version의 policy_rules를 대시보드 포맷으로 반환.
    - policy_name 주면 해당 이름 정책의 최신 버전만 조회.
    - 없으면 빈 리스트 반환.
    """
    version_id = _get_latest_onprem_version(policy_name=policy_name)
    if not version_id:
        return []

    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(
            """
            SELECT chain, proto, src, dst, dport, target, comment, state
            FROM policy_rules
            WHERE version_id = %s
            ORDER BY priority ASC, id ASC
            """,
            (version_id,),
        )
        rows = cur.fetchall() or []
        return [_map_rule_to_dashboard_format(r) for r in rows]
    finally:
        cur.close()
        conn.close()


def fetch_rules_by_version(version_id: int) -> List[Dict[str, Any]]:
    """
    (선택) 특정 version_id로 직접 조회해야 할 때 사용.
    """
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(
            """
            SELECT chain, proto, src, dst, dport, target, comment, state
            FROM policy_rules
            WHERE version_id = %s
            ORDER BY priority ASC, id ASC
            """,
            (version_id,),
        )
        rows = cur.fetchall() or []
        return [_map_rule_to_dashboard_format(r) for r in rows]
    finally:
        cur.close()
        conn.close()
