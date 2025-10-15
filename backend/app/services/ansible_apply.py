import os, subprocess, tempfile, json
from typing import List, Dict, Any
from app.services.iptables_versioning import _get_rules_by_version, get_version_header

ANSIBLE_PLAYBOOK_TEMPLATE = """---
- name: Apply iptables rules from policy version
  hosts: {host_group}
  become: yes
  gather_facts: yes

  vars:
    persist_rules_path: /etc/iptables/rules.v4

  pre_tasks:
    - name: Ensure iptables tools present (Debian/Ubuntu)
      apt:
        name:
          - iptables
          - iptables-persistent
          - netfilter-persistent
        state: present
        update_cache: yes
      when: ansible_facts['os_family'] == 'Debian'

    - name: Flush all existing rules
      iptables:
        flush: yes

    - name: Ensure SSH is open (lockout protection)
      iptables:
        chain: INPUT
        protocol: tcp
        destination_port: 22
        ctstate: NEW,ESTABLISHED
        jump: ACCEPT

  tasks:
{rule_tasks}

    - name: Set default policies
      shell: |
        iptables -P INPUT {input_policy}
        iptables -P FORWARD {forward_policy}
        iptables -P OUTPUT {output_policy}

    - name: Save iptables rules (Debian/Ubuntu)
      shell: netfilter-persistent save
      when: ansible_facts['os_family'] == 'Debian'
"""

def _render_rule_tasks(rules: List[Dict[str, Any]]) -> str:
    """
    policy_rules → Ansible iptables 모듈 task YAML 조각 생성
    - present : ensure 규칙 추가
    - absent  : state=absent로 제거
    """
    lines = []
    # 우선순위대로
    for r in sorted(rules, key=lambda x: (x["chain"], x["priority"], x["id"])):
        params = {
            "chain": r["chain"],
            "jump": r["target"],
        }
        if r.get("proto"):        params["protocol"] = r["proto"]
        if r.get("src"):          params["source"] = r["src"]
        if r.get("dst"):          params["destination"] = r["dst"]
        if r.get("sport"):        params["source_port"] = str(r["sport"])
        if r.get("dport"):        params["destination_port"] = str(r["dport"])
        if r.get("in_iface"):     params["in_interface"] = r["in_iface"]
        if r.get("out_iface"):    params["out_interface"] = r["out_iface"]
        if r.get("state_match"):  params["ctstate"] = r["state_match"]
        state_param = "present" if r["state"] == "present" else "absent"

        # 한 task
        lines.append("    - name: rule {} {} {}".format(r["chain"], r.get("proto") or "", r.get("dport") or ""))
        lines.append("      iptables:")
        for k, v in params.items():
            lines.append(f"        {k}: {v}")
        lines.append(f"        state: {state_param}")
        if r.get("comment"):
            lines.append(f"        comment: \"{r['comment']}\"")
        lines.append("")  # spacer

    return "\n".join(lines)

def _create_deployment(version_id: int, host: str) -> int:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO deployments (version_id, host, status) VALUES (%s,%s,'PENDING')", (version_id, host))
        conn.commit()
        return cur.lastrowid
    finally:
        cur.close(); conn.close()

def _update_deployment(dep_id: int, status: str, log_text: str = None):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE deployments
            SET status=%s, applied_at=IF(%s IN ('SUCCESS','FAILED'), NOW(), applied_at), log_text=CONCAT(COALESCE(log_text,''), %s)
            WHERE id=%s
        """, (status, status, log_text or "", dep_id))
        conn.commit()
    finally:
        cur.close(); conn.close()

def apply_version_to_hosts(version_id: int, hosts: List[str], defaults: Dict[str,str]):
    """
    선택 버전을 지정 호스트 목록에 적용.
    defaults: {"input_policy":"DROP","forward_policy":"DROP","output_policy":"ACCEPT"}
    """
    header = get_version_header(version_id)
    if not header:
        raise ValueError("version not found")

    rules = _get_rules_by_version(version_id)
    rule_tasks_yaml = _render_rule_tasks(rules)

    playbook = ANSIBLE_PLAYBOOK_TEMPLATE.format(
        host_group="firewall_servers",  # 인벤토리 그룹명
        rule_tasks=rule_tasks_yaml,
        input_policy=(defaults.get("input_policy","DROP").upper()),
        forward_policy=(defaults.get("forward_policy","DROP").upper()),
        output_policy=(defaults.get("output_policy","ACCEPT").upper()),
    )

    # 임시 플레이북 파일 생성
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".yml") as f:
        f.write(playbook)
        play_path = f.name

    # 인벤토리는 사용처(너의 프로젝트)에 이미 존재한다고 가정
    # hosts 에 들어온 실제 호스트는 --limit 로 제어
    for host in hosts:
        dep_id = _create_deployment(version_id, host)
        _update_deployment(dep_id, "RUNNING", f"\n== Start apply to {host}\n")

        try:
            cmd = [
                "ansible-playbook",
                play_path,
                "--limit", host,
                "-i", "./inventory.ini"   # 너의 인벤토리 경로로 맞춰줘
            ]
            proc = subprocess.run(cmd, capture_output=True, text=True)
            log = "\n--- STDOUT ---\n" + (proc.stdout or "") + "\n--- STDERR ---\n" + (proc.stderr or "")
            if proc.returncode == 0:
                _update_deployment(dep_id, "SUCCESS", log)
            else:
                _update_deployment(dep_id, "FAILED", log)
        except Exception as e:
            _update_deployment(dep_id, "FAILED", f"\nException: {e}\n")

    # 임시 파일 정리
    try:
        os.unlink(play_path)
    except Exception:
        pass
