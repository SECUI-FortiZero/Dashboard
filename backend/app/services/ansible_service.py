import ansible_runner
import os
import tempfile
from dotenv import load_dotenv

load_dotenv()

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
