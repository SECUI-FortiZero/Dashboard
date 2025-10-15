from flask import Flask, request, jsonify
from log_db import insert_log_common, insert_log_onprem, insert_log_policy  # ← 통일

app = Flask(__name__)

# 온프레 로그 API
@app.route("/api/log/onprem", methods=["POST"])
def save_onprem():
    logs = request.get_json()
    if isinstance(logs, dict):
        logs = [logs]

    ids = insert_log_common("ONPREM", logs)   # 파일 기반 스텁에 기록
    insert_log_onprem(ids, logs)

    return jsonify({"status": "ok", "inserted": len(ids), "ids": ids})

# (선택) 클라우드 로그 API는 비활성 상태 유지
# @app.route("/api/log/cloud", methods=["POST"])
# def save_cloud():
#     logs = request.get_json()
#     if isinstance(logs, dict):
#         logs = [logs]
#     ids = insert_log_common("CLOUD", logs)
#     insert_log_cloud(ids, logs)
#     return jsonify({"status": "ok", "inserted": len(ids), "ids": ids})

# 온프레 정책 로그 API
@app.route("/api/log/policy", methods=["POST"])
def save_policy():
    logs = request.get_json()
    if isinstance(logs, dict):
        logs = [logs]
    inserted_ids = insert_log_policy(logs)    # 파일 기반 스텁
    return jsonify({"status": "ok", "inserted": len(inserted_ids), "ids": inserted_ids})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
