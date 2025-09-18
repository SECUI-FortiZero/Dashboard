from flask import Blueprint, request, jsonify
from app.services import ansible_service, terraform_service, log_service
from app.database import threat_logs_collection
from bson import ObjectId
import yaml

# 'api'라는 이름과 URL 접두사(/api)를 가진 Blueprint 객체를 생성합니다.
bp = Blueprint('api', __name__, url_prefix='/api')

# app/api.py (일부만)
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
        # 플랫폼별 분리
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


@bp.route('/policy/current', methods=['GET'])
def get_current_policy_route():
    """현재 온프레미스와 클라우드에 적용된 정책을 조회합니다."""
    try:
        on_prem_rules = ansible_service.fetch_rules()
        aws_rules = terraform_service.fetch_rules()

        return jsonify({
            "status": "success",
            "data": {
                "on_premise": on_prem_rules,
                "aws": aws_rules
            }
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@bp.route('/logs/ingest', methods=['POST'])
def ingest_log_route():
    """외부 로그 수집기로부터 로그를 수신하여 DB에 저장하고 AI 분석을 요청합니다."""
    log_data = request.json
    if not log_data or 'message' not in log_data:
        return jsonify({"status": "error", "message": "Log message is required."}), 400
    try:
        log_id = log_service.save_and_analyze_log(log_data)
        return jsonify({"status": "success", "message": "Log received.", "log_id": log_id}), 202
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@bp.route('/logs/threats', methods=['GET'])
def get_threats_route():
    """AI가 위협으로 판단한 로그 목록을 반환합니다."""
    try:
        threats = list(threat_logs_collection.find({}))
        # MongoDB의 ObjectId를 문자열로 변환하여 JSON 응답 생성
        for threat in threats:
            threat['_id'] = str(threat['_id'])
            if 'original_log_id' in threat:
                threat['original_log_id'] = str(threat['original_log_id'])
        return jsonify({"status": "success", "data": threats}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500