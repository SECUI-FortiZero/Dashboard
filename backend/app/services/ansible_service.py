import ansible_runner
import os
import tempfile

def apply_rules(rules):
    """Ansible 플레이북을 실행하여 iptables 규칙을 적용합니다."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # .env 파일의 정보를 바탕으로 inventory 파일 동적 생성
        inventory_content = f"""
[firewall_servers]
{os.getenv('ONPREM_HOST')} ansible_user={os.getenv('ONPREM_USER')} ansible_ssh_private_key_file={os.path.expanduser(os.getenv('ONPREM_SSH_KEY_PATH'))}
"""
        inventory_path = os.path.join(tmpdir, 'inventory.ini')
        with open(inventory_path, 'w') as f:
            f.write(inventory_content)

        playbook_path = 'ansible/playbook_apply.yml'
        
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
    """Ansible을 사용하여 현재 iptables 규칙을 가져옵니다."""
    # (실제 구현 시에는 playbook_fetch.yml을 만들고 iptables-save 결과를 파싱해야 합니다)
    # 여기서는 개념 설명을 위해 더미 데이터를 반환합니다.
    return [
        {"platform": "on-premise", "rule": "-p tcp -m tcp --dport 22 -j ACCEPT", "comment": "SSH access"},
        {"platform": "on-premise", "rule": "-p tcp -m tcp --dport 80 -j ACCEPT", "comment": "HTTP access"}
    ]