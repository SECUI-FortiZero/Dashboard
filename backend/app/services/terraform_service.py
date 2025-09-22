import json
import subprocess
import os
import boto3
from collections import defaultdict
import tempfile
import shutil

# 원본 Terraform 파일들이 있는 템플릿 경로
TERRAFORM_TEMPLATE_DIR = 'terraform'

# 환경변수 기본값 (가능하면 .env에 설정 권장)
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "ap-northeast-2")
AWS_VPC_ID = os.getenv("AWS_VPC_ID", "vpc-0fc8c284cdbf5306d")  # ← 실제 VPC ID로 교체 권장


def _convert_rule_to_dict(rule, ec2_client):
    """Boto3 응답 규칙을 YAML과 유사한 dict 형식으로 변환하는 헬퍼 함수"""
    # 프로토콜이 -1(ALL)인 경우 포트가 없을 수 있음 → 표시용 포트 0-0로 정규화
    from_port = rule.get('FromPort', 0)
    to_port = rule.get('ToPort', from_port)
    port = f"{from_port}-{to_port}" if to_port != from_port else from_port

    # IP 기반 규칙 처리
    if rule.get('IpRanges'):
        ip_range = rule['IpRanges'][0]
        return {
            "comment": ip_range.get('Description', ''),
            "protocol": rule.get('IpProtocol'),
            "port": port,
            "source_ip": ip_range.get('CidrIp')
        }

    # 보안 그룹 기반 규칙 처리
    if rule.get('UserIdGroupPairs'):
        group_pair = rule['UserIdGroupPairs'][0]
        try:
            sg_info = ec2_client.describe_security_groups(GroupIds=[group_pair.get('GroupId')])
            sg_name = sg_info['SecurityGroups'][0]['GroupName']
        except Exception:
            sg_name = group_pair.get('GroupId')  # 실패 시 ID 사용
        return {
            "comment": group_pair.get('Description', ''),
            "protocol": rule.get('IpProtocol'),
            "port": port,
            "source_sg": sg_name
        }
    return None


def _fetch_rules_for_sg(sg_name, ec2_client):
    """특정 보안 그룹의 현재 인바운드 규칙을 읽어오는 헬퍼 함수"""
    try:
        response = ec2_client.describe_security_groups(
            Filters=[
                {"Name": "group-name", "Values": [sg_name]},
                {"Name": "vpc-id", "Values": [AWS_VPC_ID]},
            ]
        )
        if not response['SecurityGroups']:
            return []

        sg = response['SecurityGroups'][0]
        existing_rules = []
        for rule in sg.get('IpPermissions', []):
            converted_rule = _convert_rule_to_dict(rule, ec2_client)
            if converted_rule:
                existing_rules.append(converted_rule)
        return existing_rules
    except Exception:
        # 보안 그룹이 아직 없으면 빈 리스트 반환
        return []


def _auto_import_existing_rules(tmp_dir, rules):
    """AWS에 이미 존재하는 규칙은 terraform import 해서 중복 생성 오류를 예방."""
    ec2 = boto3.client('ec2', region_name=AWS_REGION)

    # 이름 → SG ID 매핑
    name_to_id = {}

    target_names = sorted({r["target_sg"] for r in rules if r.get("target_sg")})
    if target_names:
        resp = ec2.describe_security_groups(
            Filters=[
                {"Name": "group-name", "Values": target_names},
                {"Name": "vpc-id", "Values": [AWS_VPC_ID]},
            ]
        )
        for sg in resp.get("SecurityGroups", []):
            name_to_id[sg["GroupName"]] = sg["GroupId"]

    source_names = sorted({r["source_sg"] for r in rules if r.get("source_sg")})
    if source_names:
        resp2 = ec2.describe_security_groups(
            Filters=[
                {"Name": "group-name", "Values": source_names},
                {"Name": "vpc-id", "Values": [AWS_VPC_ID]},
            ]
        )
        for sg in resp2.get("SecurityGroups", []):
            name_to_id[sg["GroupName"]] = sg["GroupId"]

    # 실제 존재하는 인바운드 규칙 맵 (중복 판단용)
    existing_by_key = {}
    for tgt in target_names:
        ex_rules = _fetch_rules_for_sg(tgt, ec2)
        for er in ex_rules:
            p = er.get("port")
            if isinstance(p, str) and "-" in p:
                f, t = p.split("-")
                f, t = int(f), int(t)
            else:
                f = t = int(p)

            src_token = er.get("source_ip") or er.get("source_sg") or "self"
            k = f"{tgt}_{er.get('protocol','tcp')}_{f}_{t}_{src_token}"
            existing_by_key[k] = True

    # 존재하는 규칙은 import 시도
    for r in rules:
        src_token = r.get("source_ip") or r.get("source_sg") or "self"
        key = f"{r['target_sg']}_{r['protocol']}_{r['from_port']}_{r['to_port']}_{src_token}"

        if key not in existing_by_key:
            # 실제 AWS에 없으면 import 불필요 (신규 생성 대상)
            continue

        # terraform 리소스 주소 (for_each 키와 동일)
        addr = f'aws_security_group_rule.ingress["{key}"]'

        # import ID: <sg-id>_ingress_<protocol>_<from>_<to>_<source>
        tgt_id = name_to_id.get(r["target_sg"])
        if not tgt_id:
            continue

        if r.get("source_ip"):
            src = r["source_ip"]
        elif r.get("source_sg") and r["source_sg"] in name_to_id:
            src = name_to_id[r["source_sg"]]
        else:
            continue  # 소스 정보를 못 찾으면 skip

        import_id = f"{tgt_id}_ingress_{r['protocol']}_{r['from_port']}_{r['to_port']}_{src}"

        # 이미 state에 있으면 생략하고, 없으면 import
        try:
            subprocess.run(
                ["terraform", f"-chdir={tmp_dir}", "state", "show", addr],
                check=True, capture_output=True, text=True
            )
            continue  # state에 존재
        except subprocess.CalledProcessError:
            pass

        subprocess.run(
            ["terraform", f"-chdir={tmp_dir}", "import", addr, import_id],
            check=False, capture_output=True, text=True
        )


def apply_rules(rules, mode='overwrite'):
    """Terraform을 실행하여 AWS Security Group 규칙을 적용합니다.
       - SG 본체는 유지, 규칙은 aws_security_group_rule로만 관리
       - 중복 규칙은 사전 감지하여 import(선택) 또는 생략
    """
    aws_rules = [r for r in rules if 'target_sg' in r]
    if not aws_rules:
        return {"status": "skipped", "message": "No AWS rules to apply."}

    # 1) YAML → 내부 표현 정규화
    normalized_rules = []
    managed_sg_names = set()
    for r in aws_rules:
        sg = r['target_sg']
        managed_sg_names.add(sg)

        port = r.get('port')
        if isinstance(port, str) and '-' in port:
            f, t = port.split('-')
            from_port, to_port = int(f), int(t)
        else:
            from_port = to_port = int(port)

        normalized_rules.append({
            "target_sg": sg,
            "protocol": r.get('protocol', 'tcp'),
            "from_port": from_port,
            "to_port": to_port,
            "source_ip": r.get('source_ip'),
            "source_sg": r.get('source_sg'),
            "description": r.get('comment', r.get('description', '')),
        })

    # 2) merge 모드: 실제 AWS 규칙을 읽어와 병합 (중복 제거)
    final_rules = normalized_rules
    if mode == 'merge':
        ec2 = boto3.client('ec2', region_name=AWS_REGION)
        by_key = {}

        def key_fn(x):
            return (
                x["target_sg"], x["protocol"], x["from_port"], x["to_port"],
                x.get("source_ip") or f"sg:{x.get('source_sg')}"
            )

        # 현재 규칙
        for sg_name in managed_sg_names:
            for exist in _fetch_rules_for_sg(sg_name, ec2):
                if exist.get('source_sg') or exist.get('source_ip'):
                    e_port = exist.get('port')
                    if isinstance(e_port, str) and '-' in e_port:
                        f, t = e_port.split('-')
                        ef, et = int(f), int(t)
                    else:
                        ef = et = int(e_port)

                    by_key[key_fn({
                        "target_sg": sg_name,
                        "protocol": exist.get('protocol', 'tcp'),
                        "from_port": ef,
                        "to_port": et,
                        "source_ip": exist.get('source_ip'),
                        "source_sg": exist.get('source_sg'),
                    })] = {
                        "target_sg": sg_name,
                        "protocol": exist.get('protocol', 'tcp'),
                        "from_port": ef,
                        "to_port": et,
                        "source_ip": exist.get('source_ip'),
                        "source_sg": exist.get('source_sg'),
                        "description": exist.get('comment', ''),
                    }

        # 신규 규칙
        for n in normalized_rules:
            by_key[key_fn(n)] = n
        final_rules = list(by_key.values())

    # 3) TF 변수 생성
    tf_vars = {
        "managed_sg_names": sorted(managed_sg_names),
        "sg_rules": final_rules,
        "aws_region": AWS_REGION,   # providers.tf 변수
        "aws_vpc_id": AWS_VPC_ID,   # data lookup용 VPC ID
    }

    # 4) 임시 작업 디렉터리에서 Terraform 실행 (+ 선택적 auto-import)
    AUTO_IMPORT_EXISTING = True
    with tempfile.TemporaryDirectory() as tmp_terraform_dir:
        # 필요한 .tf 및 .terraform.lock.hcl만 복사 (state는 복사하지 않음)
        for item in os.listdir(TERRAFORM_TEMPLATE_DIR):
            s = os.path.join(TERRAFORM_TEMPLATE_DIR, item)
            d = os.path.join(tmp_terraform_dir, item)
            if os.path.isfile(s) and (s.endswith('.tf') or item == '.terraform.lock.hcl'):
                shutil.copy2(s, d)

        # 변수 파일 작성
        vars_path = os.path.join(tmp_terraform_dir, 'policy.auto.tfvars.json')
        with open(vars_path, 'w') as f:
            json.dump(tf_vars, f, indent=2)

        # terraform init (에러 상세 노출)
        try:
            subprocess.run(
                ["terraform", f"-chdir={tmp_terraform_dir}", "init", "-upgrade"],
                check=True, capture_output=True, text=True
            )
        except subprocess.CalledProcessError as e:
            raise Exception(f"Terraform init failed:\nSTDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}")

        # 기존 규칙 import로 중복 에러 예방
        if AUTO_IMPORT_EXISTING:
            _auto_import_existing_rules(tmp_terraform_dir, final_rules)

        try:
            result = subprocess.run(
                ["terraform", f"-chdir={tmp_terraform_dir}", "apply", "-auto-approve"],
                check=True, capture_output=True, text=True
            )
            return {"status": "success", "output": result.stdout}
        except subprocess.CalledProcessError as e:
            raise Exception(f"Terraform execution failed:\nSTDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}")


def fetch_rules():
    """현재 관리 중인 모든 보안 그룹의 규칙을 조회합니다."""
    try:
        ec2 = boto3.client('ec2', region_name=AWS_REGION)
        response = ec2.describe_security_groups(
            Filters=[{'Name': 'vpc-id', 'Values': [AWS_VPC_ID]}]
        )
        all_rules = []
        for sg in response['SecurityGroups']:
            sg_name = sg['GroupName']
            for rule in sg.get('IpPermissions', []):
                converted_rule = _convert_rule_to_dict(rule, ec2)
                if converted_rule:
                    converted_rule['platform'] = 'aws'
                    converted_rule['target_sg'] = sg_name
                    all_rules.append(converted_rule)
        return all_rules
    except Exception as e:
        raise Exception(f"Failed to fetch AWS rules: {str(e)}")
