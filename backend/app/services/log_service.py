#from app.database import raw_logs_collection
#from app.tasks import analyze_log_task
from app.connetor_db import get_connection
from datetime import datetime
import json
from app.connector_db import get_connection
import json

def normalize_log(row):
    """raw_log JSON을 공통 필드(srcip, dstip, srcport, dstport, protocol, action)로 변환"""
    log_type = row["log_type"].upper()
    try:
        raw = json.loads(row["raw_log"]) if row["raw_log"] else {}
    except Exception:
        raw = {"error": "invalid_json", "raw": row["raw_log"]}

    if log_type == "CLOUD":
        return {
            "id": row["id"],
            "timestamp": row["timestamp"].isoformat() if row["timestamp"] else None,
            "log_type": log_type,
            "srcip": raw.get("srcaddr"),
            "dstip": raw.get("dstaddr"),
            "srcport": raw.get("srcport"),
            "dstport": raw.get("dstport"),
            "protocol": raw.get("protocol"),
            "action": raw.get("action"),
        }
    elif log_type == "ONPREM":
        return {
            "id": row["id"],
            "timestamp": row["timestamp"].isoformat() if row["timestamp"] else None,
            "log_type": log_type,
            "srcip": raw.get("SRC"),
            "dstip": raw.get("DST"),
            "srcport": raw.get("SPT"),
            "dstport": raw.get("DPT"),
            "protocol": raw.get("PROTO"),
            "action": None,  # 온프레미스 로그에는 action 없음
        }
    else:
        # 알 수 없는 타입 → 원본 그대로 반환
        raw.update({
            "id": row["id"],
            "timestamp": row["timestamp"].isoformat() if row["timestamp"] else None,
            "log_type": log_type
        })
        return raw


def get_logs(limit=50, log_type=None):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    sql = "SELECT id, timestamp, log_type, raw_log FROM log_common"
    params = []
    if log_type:
        sql += " WHERE log_type = %s"
        params.append(log_type.upper())
    sql += " ORDER BY timestamp DESC LIMIT %s"
    params.append(limit)

    cursor.execute(sql, params)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    # ✅ 여기서 normalize 처리
    return [normalize_log(row) for row in rows]
