# app/routes.py
from flask import Blueprint, request, jsonify
from datetime import datetime
import yaml

from app.services import ansible_service, terraform_service, log_service

# iptables 버전관리 서비스
from app.services.iptables_versioning import (
    save_policy_version,
    diff_versions,
    get_version_header,
)
from app.services.ansible_apply import apply_version_to_hosts

bp = Blueprint("api", __name__, url_prefix="/api")


# ==============================
# 대시보드 YAML → 버전관리 YAML(온프레만) 변환 헬퍼
# ==============================
def _dashboard_yaml_to_version_yaml(
    on_prem_rules: list, policy_name: str, author: str, message: str | None = None
) -> str:
    """
    대시보드 YAML의 on-premise 규칙들을 버전관리 YAML 형식으로 변환.
    INPUT: [{"platform":"on-premise","chain":..., "protocol":..., "port":..., "source_ip":..., "destination_ip":..., "action":..., "comment":..., "state":(선택)} ...]
    OUTPUT: iptables_versioning이 기대하는 YAML 문자열
    """
    import yaml as _yaml

    payload = {
        "policy": {
            "name": policy_name or "onprem-main",
            "author": author or "unknown",
            "message": message
            or f"Applied via /policy/apply at {datetime.now().isoformat(timespec='seconds')}",
        },
        "defaults": {"table": "filter"},
        "rules": [],
    }

    for r in on_prem_rules:
        if r.get("platform") != "on-premise":
            continue

        chain = (r.get("chain") or "INPUT").upper()
        target = (r.get("action") or "ACCEPT").upper()  # 대시보드 action -> iptables target

        vr = {
            "chain": chain,
            "target": target,
            "priority": int(r.get("priority", 100)),
        }
        if r.get("protocol"):
            vr["proto"] = str(r["protocol"])
        if r.get("port") is not None:
            vr["dport"] = str(r["port"])
        if r.get("source_ip"):
            vr["src"] = str(r["source_ip"])
        if r.get("destination_ip"):
            vr["dst"] = str(r["destination_ip"])
        if r.get("comment"):
            vr["comment"] = str(r["comment"])
        if r.get("state") in ("present", "absent"):
            vr["state"] = r["state"]

        payload["rules"].append(vr)

    return _yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)


# ==============================
# 기존 정책 적용 (on-prem / aws)
# ==============================
@bp.route("/policy/apply", methods=["POST"])
def apply_policy_route():
    if "policy_file" not in request.files:
        return jsonify({"status": "error", "message": "정책 YAML 파일이 필요합니다."}), 400

    file = request.files["policy_file"]
    try:
        policy_data = yaml.safe_load(file.stream)
        if not isinstance(policy_data, dict):
            return jsonify({"status": "error", "message": "잘못된 YAML 형식입니다."}), 400

        all_rules = policy_data.get("rules", [])
        if not isinstance(all_rules, list):
            return jsonify({"status": "error", "message": "rules는 리스트여야 합니다."}), 400

        default_policy = policy_data.get("default", {})
        on_prem_rules = [r for r in all_rules if r.get("platform") == "on-premise"]
        aws_rules = [r for r in all_rules if r.get("platform") == "aws"]

        results: dict = {}

        # 온프레 적용
        if on_prem_rules:
            results["on_premise"] = ansible_service.apply_rules(
                rules=on_prem_rules,
                default_policy=default_policy,
                policy_name=policy_data.get("policy_name", "unnamed"),
            )

            # 🔽 온프레만 버전관리 스냅샷 저장 (실패해도 적용은 성공 처리)
            try:
                version_yaml = _dashboard_yaml_to_version_yaml(
                    on_prem_rules=on_prem_rules,
                    policy_name=policy_data.get("policy_name", "onprem-main"),
                    author=policy_data.get("author", "dashboard"),
                    message=policy_data.get("message") or policy_data.get("commit_msg"),
                )
                _, version_id = save_policy_version(version_yaml)
                results["on_premise_version_id"] = version_id
            except Exception as ve:
                results["on_premise_version_error"] = str(ve)

        # AWS 적용
        if aws_rules:
            results["aws"] = terraform_service.apply_rules(aws_rules)

        return (
            jsonify(
                {"status": "success", "message": "정책 적용이 완료되었습니다.", "details": results}
            ),
            200,
        )
    except Exception as e:
        return jsonify({"status": "error", "message": f"Apply failed: {e}"}), 500


# ==============================
# 현재 정책 조회
# ==============================
@bp.route("/policy/current", methods=["GET"])
def get_current_policy_route():
    try:
        on_prem_rules = ansible_service.fetch_rules()
        aws_rules = terraform_service.fetch_rules()
        return (
            jsonify(
                {"status": "success", "data": {"on_premise": on_prem_rules, "aws": aws_rules}}
            ),
            200,
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ==============================
# 로그 인입 (MySQL 기반 log_service 사용 가정)
# ==============================
@bp.route("/logs/ingest", methods=["POST"])
def ingest_log_route():
    log_data = request.json
    if not log_data or "message" not in log_data:
        return jsonify({"status": "error", "message": "Log message is required."}), 400
    try:
        log_id = log_service.save_and_analyze_log(log_data)
        return jsonify({"status": "success", "message": "Log received.", "log_id": log_id}), 202
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ==============================
# 로그 조회 (간단 API)
# ==============================
@bp.route("/logs", methods=["GET"])
def get_logs_route():
    log_type = request.args.get("type")
    limit = request.args.get("limit", 50, type=int)
    try:
        logs = log_service.get_logs(limit=limit, log_type=log_type)
        return jsonify({"status": "success", "data": logs}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ==============================
# iptables 정책 "버전관리" API
# ==============================

# 1) 버전 생성/저장: YAML 업로드 → 스냅샷 저장
@bp.route("/iptables/version", methods=["POST"])
def create_iptables_version_route():
    """
    Form:
      - policy_file(파일) 또는 yaml_text(text/json)
    Return:
      { status, policy_id, version_id }
    """
    yaml_text = None
    if "policy_file" in request.files:
        yaml_text = request.files["policy_file"].read().decode("utf-8")
    else:
        if request.is_json:
            yaml_text = (request.json or {}).get("yaml_text")
        else:
            yaml_text = request.form.get("yaml_text")

    if not yaml_text:
        return jsonify({"status": "error", "message": "YAML이 필요합니다."}), 400

    try:
        policy_id, version_id = save_policy_version(yaml_text)
        return jsonify({"status": "ok", "policy_id": policy_id, "version_id": version_id}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


# 2) 버전 간 Diff 조회: base vs new
@bp.route("/iptables/diff", methods=["GET"])
def get_iptables_diff_route():
    """
    Query:
      ?base=<version_id>&new=<version_id>
    Return:
      { status, diff: { added, removed, changed, kept } }
    """
    base_id = request.args.get("base", type=int)
    new_id = request.args.get("new", type=int)
    if not base_id or not new_id:
        return jsonify({"status": "error", "message": "base, new 파라미터가 필요합니다."}), 400

    try:
        d = diff_versions(base_id, new_id)
        return jsonify({"status": "ok", "diff": d}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


# 3) 특정 버전 메타 조회
@bp.route("/iptables/versions/<int:version_id>", methods=["GET"])
def get_iptables_version_meta_route(version_id: int):
    header = get_version_header(version_id)
    if not header:
        return jsonify({"status": "error", "message": "not found"}), 404
    return jsonify({"status": "ok", "version": header}), 200


# 4) 버전 적용(배포)
@bp.route("/iptables/apply", methods=["POST"])
def apply_iptables_version_route():
    """
    JSON:
    {
      "version_id": 123,
      "hosts": ["192.168.5.10"],
      "defaults": {"input_policy":"DROP","forward_policy":"DROP","output_policy":"ACCEPT"}
    }
    """
    data = request.get_json(silent=True) or {}
    version_id = data.get("version_id")
    hosts = data.get("hosts") or []
    defaults = data.get("defaults") or {}

    if not version_id or not hosts:
        return jsonify({"status": "error", "message": "version_id와 hosts가 필요합니다."}), 400

    try:
        apply_version_to_hosts(version_id, hosts, defaults)
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
