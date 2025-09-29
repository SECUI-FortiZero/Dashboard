#from app.database import raw_logs_collection
#from app.tasks import analyze_log_task
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
            "id": row["log_id"],
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
            "id": row["log_id"],
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
            "id": row["log_id"],
            "timestamp": row["timestamp"].isoformat() if row["timestamp"] else None,
            "log_type": log_type
        })
        return raw


def get_logs_by_range(range_type="daily"):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if range_type == "daily":
        date_filter = "NOW() - INTERVAL 1 DAY"
    elif range_type == "weekly":
        date_filter = "NOW() - INTERVAL 7 DAY"
    elif range_type == "monthly":
        date_filter = "NOW() - INTERVAL 1 MONTH"
    elif range_type == "hour":
        date_filter = "NOW() - INTERVAL 1 HOUR"
    elif range_type == "10min":
        date_filter = "NOW() - INTERVAL 10 MINUTE"
    else:
        raise ValueError("Invalid range type")

    sql = f"""
        SELECT log_id, log_type, raw_log
        FROM log_common
        WHERE timestamp >= {date_filter}
        ORDER BY log_id DESC
    """

    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    # ✅ normalize 처리
    return [normalize_log(row) for row in rows]
