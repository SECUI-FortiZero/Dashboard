from flask import Blueprint, request, jsonify
from bson import ObjectId
import yaml

# 전역 app를 쓰지 않고 블루프린트로 정의
bp = Blueprint("main", __name__)

# 지연 import: Windows에서 ansible_runner(fcntl 문제) 우회 + 순환 import 방지
def _svc():
    from app.services import ansible_service, terraform_service, log_service
    from app.database import threat_logs_collection
    return ansible_service, terraform_service, log_service, threat_logs_collection

@bp.post('/api/policy/apply')
def apply_policy_route():
    if 'policy_file' not in request.files:
        return jsonify({"status": "error", "message": "정책 YAML 파일이 필요합니다."}), 400
    file = request.files['policy_file']

    try:
        policy_data = yaml.safe_load(file.stream) or {}
        all_rules = policy_data.get('rules', [])
        on_prem_rules = [r for r in all_rules if r.get('platform') == 'on-premise']
        aws_rules     = [r for r in all_rules if r.get('platform') == 'aws']

        ansible_service, terraform_service, _, _ = _svc()
        results = {}
        if on_prem_rules:
            results['on_premise'] = ansible_service.apply_rules(on_prem_rules)
        if aws_rules:
            results['aws'] = terraform_service.apply_rules(aws_rules)

        return jsonify({"status": "success", "message": "정책 적용이 완료되었습니다.", "details": results}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@bp.get('/api/policy/current')
def get_current_policy_route():
    try:
        ansible_service, terraform_service, _, _ = _svc()
        on_prem_rules = ansible_service.fetch_rules()
        aws_rules     = terraform_service.fetch_rules()
        return jsonify({
            "status": "success",
            "data": {"on_premise": on_prem_rules, "aws": aws_rules}
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@bp.post('/api/logs/ingest')
def ingest_log_route():
    log_data = request.json
    if not log_data or 'message' not in log_data:
        return jsonify({"status": "error", "message": "Log message is required."}), 400
    try:
        _, _, log_service, _ = _svc()
        log_id = log_service.save_and_analyze_log(log_data)
        return jsonify({"status": "success", "message": "Log received.", "log_id": log_id}), 202
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@bp.get('/api/logs/threats')
def get_threats_route():
    try:
        _, _, _, threat_logs_collection = _svc()
        threats = list(threat_logs_collection.find({}))
        for t in threats:
            t['_id'] = str(t['_id'])
            if 'original_log_id' in t:
                t['original_log_id'] = str(t['original_log_id'])
        return jsonify({"status": "success", "data": threats}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
