import json
import subprocess
import os
import boto3
from collections import defaultdict

TERRAFORM_DIR = 'terraform'

def apply_rules(rules):
    rules_by_sg = defaultdict(list)
    for rule in rules:
        sg_name = rule.get('target_sg', 'hybrid-firewall-managed-sg')
        tf_rule = {
            "description": rule.get('comment', ''), "protocol": rule.get('protocol'),
            "from_port": rule.get('port'), "to_port": rule.get('port'),
            "cidr_blocks": [rule.get('source_ip', '0.0.0.0/0')]
        }
        rules_by_sg[sg_name].append(tf_rule)

    tf_vars = {"security_group_rules": dict(rules_by_sg)}
    vars_path = os.path.join(TERRAFORM_DIR, 'policy.auto.tfvars.json')
    with open(vars_path, 'w') as f:
        json.dump(tf_vars, f, indent=2)

    try:
        subprocess.run(["terraform", f"-chdir={TERRAFORM_DIR}", "init", "-upgrade"], check=True, capture_output=True, text=True)
        result = subprocess.run(["terraform", f"-chdir={TERRAFORM_DIR}", "apply", "-auto-approve"], check=True, capture_output=True, text=True)
        return {"status": "success", "output": result.stdout}
    except subprocess.CalledProcessError as e:
        raise Exception(f"Terraform execution failed:\nSTDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}")

def fetch_rules():
    try:
        ec2 = boto3.client('ec2', region_name=os.getenv("AWS_DEFAULT_REGION"))
        response = ec2.describe_security_groups(
            Filters=[{'Name': 'tag-key', 'Values': ['Name']}]
        )
        all_rules = []
        for sg in response['SecurityGroups']:
            sg_name = sg['GroupName']
            for rule in sg.get('IpPermissions', []):
                if rule.get('FromPort'):
                    for ip_range in rule.get('IpRanges', []):
                        all_rules.append({
                            "platform": "aws", "target_sg": sg_name, "protocol": rule.get('IpProtocol'),
                            "port": rule.get('FromPort'), "source_ip": ip_range.get('CidrIp'),
                            "comment": ip_range.get('Description', '')
                        })
        return all_rules
    except Exception as e:
        raise Exception(f"Failed to fetch AWS rules: {str(e)}")