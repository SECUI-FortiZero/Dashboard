from datetime import datetime
import json
from app.connector_db import get_connection

def normalize_log(row):
    """raw_log JSON을 공통 필드(srcip, dstip, srcport, dstport, protocol, action)로 변환"""
    log_type = row.get("log_type", "UNKNOWN").upper()
    try:
        raw = json.loads(row.get("raw_log") or '{}')
    except Exception:
        raw = {"error": "invalid_json", "raw": row.get("raw_log")}

    # [수정] id, timestamp 필드가 없을 경우를 대비한 방어 코드 추가
    common_data = {
        "id": row.get("log_id"),
        "timestamp": row["timestamp"].isoformat() if row.get("timestamp") else None,
        "log_type": log_type,
    }

    if log_type == "CLOUD":
        common_data.update({
            "srcip": raw.get("srcaddr"),
            "dstip": raw.get("dstaddr"),
            "srcport": raw.get("srcport"),
            "dstport": raw.get("dstport"),
            "protocol": raw.get("protocol"),
            "action": raw.get("action"),
        })
        return common_data
    elif log_type == "ONPREM":
        common_data.update({
            "srcip": raw.get("SRC"),
            "dstip": raw.get("DST"),
            "srcport": raw.get("SPT"),
            "dstport": raw.get("DPT"),
            "protocol": raw.get("PROTO"),
            "action": None,
        })
        return common_data
    else:
        raw.update(common_data)
        return raw

# [수정] routes.py 와 호환되도록 함수 전체를 수정했습니다.
def get_logs(limit=50, log_type=None):
    """
    DB에서 로그를 조회하고 정규화하여 반환합니다.
    log_type으로 필터링하고 limit으로 개수를 제한합니다.
    """
    conn, cursor = None, None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # SQL Injection을 방지하는 안전한 방식으로 쿼리 구성
        sql = "SELECT log_id, timestamp, log_type, raw_log FROM log_common"
        params = []
        
        if log_type:
            sql += " WHERE log_type = %s"
            params.append(log_type.upper())
        
        sql += " ORDER BY log_id DESC LIMIT %s"
        params.append(limit)

        cursor.execute(sql, params)
        rows = cursor.fetchall()
        
        return [normalize_log(row) for row in rows]
    finally:
        if cursor: cursor.close()
        if conn and conn.is_connected(): conn.close()