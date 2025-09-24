from flask import Flask, request, jsonify
from log_db import insert_log_common, insert_log_onprem, insert_log_policy

app = Flask(__name__)

# 온프레 로그 API
@app.route("/api/log/onprem", methods=["POST"])
def save_onprem():
    logs = request.get_json()

    # 단일 객체일 수도 있으니 리스트로 변환
    if isinstance(logs, dict):
        logs = [logs]

    # 공통 로그 & 세부 로그 저장
    ids = insert_log_common("ONPREM", logs)
    insert_log_onprem(ids, logs)

    return jsonify({"status": "ok", "inserted": len(ids), "ids": ids})

'''
# 클라우드 로그 API
@app.route("/api/log/cloud", methods=["POST"])
def save_cloud():
    logs = request.get_json()

    if isinstance(logs, dict):
        logs = [logs]

    ids = insert_log_common("CLOUD", logs)
    insert_log_cloud(ids, logs)

    return jsonify({"status": "ok", "inserted": len(ids), "ids": ids})
'''

# 온프레 정책 로그 API
@app.route("/api/log/policy", methods=["POST"])
def save_policy():
    logs = request.get_json()

    # 단일 객체일 수도 있으니 리스트로 변환
    if isinstance(logs, dict):
        logs = [logs]

    inserted_ids = insert_log_policy(logs)

    return jsonify({"status": "ok", "inserted": len(inserted_ids), "ids": inserted_ids})



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
