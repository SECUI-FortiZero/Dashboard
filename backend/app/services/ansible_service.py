import ansible_runner
import os
import tempfile

def apply_rules(rules):
    """Ansible 플레이북을 실행하여 iptables 규칙을 적용합니다."""
    
    # 현재 파일의 위치를 기준으로 프로젝트 루트 경로를 계산합니다.
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # 프로젝트 루트로부터의 절대 경로를 만듭니다.
    playbook_path = os.path.join(project_root, 'ansible', 'playbook_apply.yml')

    with tempfile.TemporaryDirectory() as tmpdir:
        inventory_content = f"""
[firewall_servers]
{os.getenv('ONPREM_HOST')} ansible_user={os.getenv('ONPREM_USER')} ansible_ssh_private_key_file={os.path.expanduser(os.getenv('ONPREM_SSH_KEY_PATH'))}
"""
        inventory_path = os.path.join(tmpdir, 'inventory.ini')
        with open(inventory_path, 'w') as f:
            f.write(inventory_content)

        # playbook_path = 'ansible/playbook_apply.yml' # <--- 이 줄을 삭제하세요!
        
        runner = ansible_runner.run(
            private_data_dir=tmpdir,
            playbook=playbook_path,
            inventory=inventory_path,
            extravars={'rules_from_api': rules}
        )
        if runner.rc != 0:
            raise Exception(f"Ansible playbook failed. Status: {runner.status}")
        return {"status": "success", "changed_hosts": runner.stats.get('ok', {})}

def fetch_rules():
    # 실제 구현 시에는 iptables-save 결과를 파싱하는 로직이 필요합니다.
    return [{"platform": "on-premise", "rule": "-p tcp -m tcp --dport 22 -j ACCEPT"}]