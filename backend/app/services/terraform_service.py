# app/services/terraform_service.py (수정 후)

import json
import subprocess
import os
import boto3
from collections import defaultdict

TERRAFORM_DIR = 'terraform'

# --- 기존 apply_rules 함수는 그대로 둡니다 ---
def apply_rules(rules):
    # ... (기존 코드와 동일) ...
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

# --- [신규] 현재 AWS 상태를 조회하는 함수들 ---

def _fetch_sg_rules(client):
    """보안 그룹 규칙을 조회하는 내부 헬퍼 함수"""
    all_rules = []
    paginator = client.get_paginator('describe_security_groups')
    for page in paginator.paginate(Filters=[{'Name': 'tag-key', 'Values': ['Name']}]):
        for sg in page['SecurityGroups']:
            sg_name = sg['GroupName']
            for rule in sg.get('IpPermissions', []):
                if rule.get('FromPort') is not None:
                    for ip_range in rule.get('IpRanges', []):
                        all_rules.append({
                            "platform": "aws", "target_sg": sg_name, "protocol": rule.get('IpProtocol'),
                            "port": rule.get('FromPort'), "source_ip": ip_range.get('CidrIp'),
                            "comment": ip_range.get('Description', '')
                        })
    return all_rules

def _fetch_iam_data(client):
    """IAM 사용자, 그룹, 정책 정보를 조회하는 내부 헬퍼 함수"""
    iam_data = {"users": [], "groups": []}
    
    # IAM 사용자 및 소속 그룹, 정책 조회
    user_paginator = client.get_paginator('list_users')
    for page in user_paginator.paginate():
        for user in page['Users']:
            user_info = {
                "name": user['UserName'],
                "arn": user['Arn'],
                "user_id": user['UserId'],
                "groups": [],
                "attached_policies": []
            }
            # 사용자가 속한 그룹 조회
            groups_response = client.list_groups_for_user(UserName=user['UserName'])
            user_info["groups"] = [g['GroupName'] for g in groups_response.get('Groups', [])]
            
            # 사용자에게 직접 연결된 정책 조회
            policies_paginator = client.get_paginator('list_attached_user_policies')
            for policy_page in policies_paginator.paginate(UserName=user['UserName']):
                user_info["attached_policies"].extend([p['PolicyName'] for p in policy_page.get('AttachedPolicies', [])])
            
            iam_data["users"].append(user_info)
            
    # IAM 그룹 및 연결된 정책 조회
    group_paginator = client.get_paginator('list_groups')
    for page in group_paginator.paginate():
        for group in page['Groups']:
            group_info = {
                "name": group['GroupName'],
                "arn": group['Arn'],
                "group_id": group['GroupId'],
                "attached_policies": []
            }
            # 그룹에 연결된 정책 조회
            policies_paginator = client.get_paginator('list_attached_group_policies')
            for policy_page in policies_paginator.paginate(GroupName=group['GroupName']):
                group_info["attached_policies"].extend([p['PolicyName'] for p in policy_page.get('AttachedPolicies', [])])
            
            iam_data["groups"].append(group_info)
            
    return iam_data

def fetch_current_aws_state():
    """EC2 보안 그룹과 IAM 관련 정보를 모두 조회하여 반환하는 메인 함수"""
    try:
        region = os.getenv("AWS_DEFAULT_REGION", "ap-northeast-2")
        ec2_client = boto3.client('ec2', region_name=region)
        iam_client = boto3.client('iam') # IAM은 Global 서비스이므로 region 불필요

        sg_rules = _fetch_sg_rules(ec2_client)
        iam_data = _fetch_iam_data(iam_client)

        return {
            "security_group_rules": sg_rules,
            "iam_users": iam_data["users"],
            "iam_groups": iam_data["groups"]
        }
    except Exception as e:
        raise Exception(f"Failed to fetch AWS current state: {str(e)}")

# [참고] 기존 fetch_rules 함수는 이제 사용되지 않으므로 삭제하거나,
# 호환성을 위해 남겨두려면 아래와 같이 수정할 수 있습니다.
def fetch_rules():
    """기존 fetch_rules와의 호환성을 위한 함수"""
    region = os.getenv("AWS_DEFAULT_REGION", "ap-northeast-2")
    ec2_client = boto3.client('ec2', region_name=region)
    return _fetch_sg_rules(ec2_client)