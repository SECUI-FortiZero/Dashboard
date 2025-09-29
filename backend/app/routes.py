from flask import Blueprint, request, jsonify
from app.services import ansible_service, terraform_service, log_service
from app.database import threat_logs_collection  # 기존 동작 유지
from bson import ObjectId
import yaml

bp = Blueprint('api', __name__, url_prefix='/api')

# 정책 적용 (기존 동작 유지)
@bp.route('/policy/apply', methods=['POST'])
def apply_policy_route():
    if 'policy_file' not in request.files:
        return jsonify({"status": "error", "message": "정책 YAML 파일이 필요합니다."}), 400
    file = request.files['policy_file']
    try:
        policy_data = yaml.safe_load(file.stream)
        if not isinstance(policy_data, dict):
            return jsonify({"status": "error", "message": "잘못된 YAML 형식입니다."}), 400

        all_rules = policy_data.get('rules', [])
        if not isinstance(all_rules, list):
            return jsonify({"status": "error", "message": "rules는 리스트여야 합니다."}), 400

        default_policy = policy_data.get('default', {})
        on_prem_rules = [r for r in all_rules if r.get('platform') == 'on-premise']
        aws_rules     = [r for r in all_rules if r.get('platform') == 'aws']

        results = {}
        if on_prem_rules:
            results['on_premise'] = ansible_service.apply_rules(
                rules=on_prem_rules,
                default_policy=default_policy,
                policy_name=policy_data.get('policy_name', 'unnamed')
            )
        if aws_rules:
            results['aws'] = terraform_service.apply_rules(aws_rules)

        return jsonify({"status": "success", "message": "정책 적용이 완료되었습니다.", "details": results}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Apply failed: {e}"}), 500

# 현재 정책 조회 (기존 동작 유지)
@bp.route('/policy/current', methods=['GET'])
def get_current_policy_route():
    try:
        on_prem_rules = ansible_service.fetch_rules()
        aws_rules = terraform_service.fetch_rules()
        return jsonify({
            "status": "success",
            "data": {"on_premise": on_prem_rules, "aws": aws_rules}
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 로그 인입 (기존 동작 유지)
@bp.route('/logs/ingest', methods=['POST'])
def ingest_log_route():
    log_data = request.json
    if not log_data or 'message' not in log_data:
        return jsonify({"status": "error", "message": "Log message is required."}), 400
    try:
        log_id = log_service.save_and_analyze_log(log_data)
        return jsonify({"status": "success", "message": "Log received.", "log_id": log_id}), 202
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 위협 로그 조회 (기존 동작 유지)
@bp.route('/logs/threats', methods=['GET'])
def get_threats_route():
    try:
        threats = list(threat_logs_collection.find({}))
        for threat in threats:
            threat['_id'] = str(threat['_id'])
            if 'original_log_id' in threat:
                threat['original_log_id'] = str(threat['original_log_id'])
        return jsonify({"status": "success", "data": threats}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# feat/#10: DB에서 log_common 조회하는 간단 API 추가(기존 동작에 영향 없음)
@bp.route('/logs', methods=['GET'])
def get_logs_route():
    log_type = request.args.get("type")
    limit = request.args.get("limit", 50, type=int)
    try:
        logs = log_service.get_logs(limit=limit, log_type=log_type)
        return jsonify({"status": "success", "data": logs}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
