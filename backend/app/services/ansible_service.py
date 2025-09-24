import ansible_runner
import os
import tempfile
import subprocess
import shlex
import re
import base64
import json
from dotenv import load_dotenv

load_dotenv()

# ===== 기존 apply_rules (그대로) =====
def apply_rules(rules, default_policy=None, policy_name="unnamed"):
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    playbook_path = os.path.join(project_root, 'ansible', 'playbook_apply.yml')

    host = os.getenv('ONPREM_HOST', '192.168.5.10')
    user = os.getenv('ONPREM_USER', 'linux')
    key  = os.getenv('ONPREM_SSH_KEY_PATH', '/home/soobin/.ssh/id_rsa')
    port = os.getenv('ONPREM_PORT', '22')

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
            'ansible_become_password': os.getenv('ONPREM_BECOME_PASS', '')
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
            ident = getattr(r, 'ident', None) or 'unknown'
            stdout_path = os.path.join(tmpdir, 'artifacts', ident, 'stdout')
            err_txt = ""
            try:
                with open(stdout_path, 'r', encoding='utf-8', errors='ignore') as f:
                    err_txt = f.read()
            except Exception:
                err_txt = str(getattr(r, 'status', 'failed'))

            raise Exception(f"Ansible playbook failed (rc={r.rc}): {err_txt}")

        summary = getattr(r, 'stats', {})
        return {"status": "success", "rc": r.rc, "summary": summary}


# ====== 여기서부터 추가: iptables-save 파서 + fetch_rules ======
# === 추가 유틸: Ansible 한 줄 stdout 추출 & base64 디코더 ===

def _extract_stdout_from_ansible_minimal(raw: str) -> str:
    """
    ansible -o 출력에서 (stdout) 섹션만 안전하게 추출.
    여러 호스트/줄이 있어도 첫 번째 stdout 덩어리만 사용.
    """
    # 가장 흔한 포맷: "IP | SUCCESS | rc=0 | (stdout) <PAYLOAD>\nIP | SUCCESS | ... (stderr) ..."
    m = re.search(r"\|\s*\(stdout\)\s*(.*)", raw, re.DOTALL)
    if m:
        # 다음 (stderr) 블록 시작 전까지만 자르기
        out = m.group(1)
        m2 = re.search(r"\n.*\|\s*\(stderr\)\s*", out)
        if m2:
            out = out[:m2.start()]
        return out.strip()

    # JSON 콜백 등 다른 콜백일 때(혹시 모를 대비)
    # stdout 값만 찾아보기
    try:
        data = json.loads(raw)
        # ad-hoc json 콜백은 보통 {"contacted": {"host": {"stdout": "..."}}} 같은 형태가 대부분
        for k, v in data.items():
            if isinstance(v, dict):
                for hk, hv in v.items():
                    if isinstance(hv, dict) and "stdout" in hv:
                        return hv["stdout"]
    except Exception:
        pass

    # 마지막 fallback: 그대로 반환
    return raw.strip()


def _b64_decode(s: str) -> str:
    s = s.strip()
    # 공백/개행 제거
    s = "".join(s.split())
    try:
        return base64.b64decode(s).decode("utf-8", errors="ignore")
    except Exception:
        return ""

# === iptables-save -t filter 파서 ===

def _parse_filter_table(raw: str):
    """
    iptables-save -t filter 출력에서 모든 체인의 모든 규칙을 파싱한다.
    - 기본 정책(:INPUT ACCEPT ...)도 'type': 'policy'로 반환
    - 규칙(-A ...)은 포트/프로토콜 없을 때도 포함
      * protocol 기본값: "all"
      * port 기본값: "any"
    - multiport, state/conntrack, comment, in/out iface 지원
    """
    if not raw:
        return []

    lines = raw.splitlines()
    in_filter = False
    current_chain = None
    results = []

    def flush_policy(line):
        # 예: ":INPUT ACCEPT [0:0]"
        m = re.match(r"^:([A-Z0-9_+-]+)\s+([A-Z]+)\s+\[\d+:\d+\]$", line.strip())
        if not m:
            return
        chain, policy = m.group(1), m.group(2)
        results.append({
            "platform": "on-premise",
            "type": "policy",
            "chain": chain,
            "policy": policy
        })

    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if line == "*filter":
            in_filter = True
            continue
        if line == "COMMIT":
            # 테이블 끝
            if in_filter:
                in_filter = False
            continue
        if not in_filter:
            continue

        # 기본 정책 라인 처리
        if line.startswith(":"):
            flush_policy(line)
            continue

        # 규칙 라인 처리
        if not line.startswith("-A "):
            continue

        # 안전한 토큰 분리 (주석 문자열 포함 가능)
        try:
            tokens = shlex.split(line)
        except Exception:
            tokens = line.split()

        # -A <CHAIN>
        # 예: -A FORWARD -s 192.168.5.40/32 -d 3.37.200.119/32 -p tcp --dport 22 -j ACCEPT -m comment --comment "Allow..."
        if len(tokens) < 3:
            continue

        # 초기값
        rule = {
            "platform": "on-premise",
            "chain": tokens[1],
            "protocol": "all",
            "action": None,
            "port": "any",             # dport/sport 미지정 시 "any"
        }
        current_chain = rule["chain"]

        i = 2
        # 누적 포트(단일/범위/멀티 전부 문자열 표준화)
        dports = []
        sports = []
        # 멀티포트는 콤마 목록으로, 단일 --dport/--sport는 개별 숫자/범위
        while i < len(tokens):
            t = tokens[i]

            if t == "-p" and i + 1 < len(tokens):
                rule["protocol"] = tokens[i+1].lower()
                i += 2; continue

            if t == "-s" and i + 1 < len(tokens):
                rule["source_ip"] = tokens[i+1]
                i += 2; continue

            if t == "-d" and i + 1 < len(tokens):
                rule["destination_ip"] = tokens[i+1]
                i += 2; continue

            if t == "-i" and i + 1 < len(tokens):
                rule["in_iface"] = tokens[i+1]
                i += 2; continue

            if t == "-o" and i + 1 < len(tokens):
                rule["out_iface"] = tokens[i+1]
                i += 2; continue

            if t == "-j" and i + 1 < len(tokens):
                rule["action"] = tokens[i+1]
                i += 2; continue

            # 모듈 관련
            if t == "-m" and i + 1 < len(tokens):
                mod = tokens[i+1].lower()
                i += 2
                # state/conntrack
                if mod in ("state", "conntrack"):
                    # --state ESTABLISHED,RELATED  또는 --ctstate ...
                    if i < len(tokens) and (tokens[i] in ("--state", "--ctstate")) and (i + 1 < len(tokens)):
                        rule["state"] = tokens[i+1]
                        i += 2
                    continue
                # multiport
                if mod == "multiport":
                    # --dports/--sports 다음에 콤마 목록
                    while i < len(tokens):
                        flag = tokens[i]
                        if flag == "--dports" and i + 1 < len(tokens):
                            dports.extend(tokens[i+1].split(","))
                            i += 2; continue
                        if flag == "--sports" and i + 1 < len(tokens):
                            sports.extend(tokens[i+1].split(","))
                            i += 2; continue
                        # 다른 플래그면 루프 종료 (외부 while로)
                        break
                    continue
                # comment
                if mod == "comment":
                    if i < len(tokens) and tokens[i] == "--comment" and (i + 1 < len(tokens)):
                        rule["comment"] = tokens[i+1]
                        i += 2
                    continue
                # 그 외 모듈은 스킵
                continue

            # 단일 포트
            if t == "--dport" and i + 1 < len(tokens):
                dports.append(tokens[i+1])
                i += 2; continue
            if t == "--sport" and i + 1 < len(tokens):
                sports.append(tokens[i+1])
                i += 2; continue

            # 기타는 한 칸 이동
            i += 1

        # 포트 표준화:
        # 1) dports 우선, 없으면 sports 사용
        # 2) "80", "30000:30009" → "30000-30009"
        # 3) 여러 개면 "22,80,443" 형식
        def _norm_port_list(plist):
            out = []
            for p in plist:
                pr = p.replace(":", "-")
                out.append(pr)
            return out

        final_port = None
        if dports:
            nd = _norm_port_list(dports)
            final_port = nd[0] if len(nd) == 1 else ",".join(nd)
        elif sports:
            ns = _norm_port_list(sports)
            final_port = ns[0] if len(ns) == 1 else ",".join(ns)
        else:
            final_port = "any"

        # 숫자 문자열만 있으면 int로 캐스팅(단일 포트일 때만)
        if final_port != "any" and "," not in final_port and "-" not in final_port:
            try:
                final_port = int(final_port)
            except Exception:
                pass

        rule["port"] = final_port

        # action(타깃)이 없을 수도 있지만, 그래도 규칙은 보여주자
        results.append(rule)

    return results



# === 여기를 기존 fetch_rules() 대체 ===
def fetch_rules():
    """
    원격 방화벽에서 iptables 규칙을 가져온다.
    - sudo(become) 강제 사용
    - iptables-save, iptables-nft-save, iptables-legacy-save 순으로 시도
    - 결과는 base64로 인코딩하여 안전하게 수신
    - INPUT/OUTPUT/FORWARD의 tcp/udp + dport/dports 규칙을 전부 파싱
    """
    host = os.getenv('ONPREM_HOST', '192.168.5.10')
    user = os.getenv('ONPREM_USER', 'linux')
    key  = os.getenv('ONPREM_SSH_KEY_PATH', '/home/soobin/.ssh/id_rsa')
    port = os.getenv('ONPREM_PORT', '22')
    become_pass = os.getenv('ONPREM_BECOME_PASS', '')

    with tempfile.TemporaryDirectory() as tmpdir:
        inventory_content = f"""
[firewall_servers]
{host} ansible_user={user} ansible_port={port} ansible_ssh_private_key_file={key}
"""
        inventory_path = os.path.join(tmpdir, 'inventory.ini')
        with open(inventory_path, 'w') as f:
            f.write(inventory_content)

        # 한 줄 base64로 보내기 (-w0 없으면 tr -d로 대체)
        remote_cmd = r'''bash -lc '(iptables-save -t filter || iptables-nft-save -t filter || iptables-legacy-save -t filter || true) | (base64 -w0 2>/dev/null || base64 | tr -d "\n")' '''

        cmd = [
            "ansible", "firewall_servers",
            "-i", inventory_path,
            "-m", "shell",
            "-a", remote_cmd,
            "-o",           # minimal callback
            "-b"            # 항상 sudo
        ]
        if become_pass:
            cmd += ["-e", f"ansible_become_password={become_pass}"]
        cmd += ["-e", "ansible_become=true", "-e", "ansible_become_method=sudo"]

        try:
            r = subprocess.run(cmd, check=True, capture_output=True, text=True)
            raw = r.stdout or ""
            b64 = _extract_stdout_from_ansible_minimal(raw)
            decoded = _b64_decode(b64)

            # 디코드가 비었으면 규칙이 없거나(진짜 empty) 다른 테이블 사용 가능성
            # 그래도 파서 호출(빈 리스트 반환)
            rules = _parse_filter_table(decoded)

            return rules

        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to fetch on-prem rules via Ansible: {e.stderr or e.stdout}")
