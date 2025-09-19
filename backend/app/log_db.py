# log_db.py
import os
import json
import mysql.connector
from datetime import datetime


def get_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DB"),
    )


def insert_log_common(log_type: str, ts_or_list, raw=None):
    ids = []
    conn = get_connection()
    cursor = conn.cursor()

    def parse_common_time(item):
        raw_ts = item.get("readable_time") or item.get("timestamp") or item.get("time")
        if raw_ts:
            try:
                if "T" in raw_ts:  # ISO8601
                    return datetime.fromisoformat(raw_ts.replace("Z", "+00:00"))
                else:
                    return datetime.strptime(f"{datetime.utcnow().year} {raw_ts}", "%Y %b %d %H:%M:%S")
            except Exception:
                return datetime.utcnow()
        return datetime.utcnow()

    try:
        if isinstance(ts_or_list, list):
            for item in ts_or_list:
                ts = parse_common_time(item)
                sql = """
                    INSERT INTO log_common (log_type, timestamp, raw_log, created_at)
                    VALUES (%s, %s, %s, NOW())
                """
                cursor.execute(sql, (log_type, ts, json.dumps(item, ensure_ascii=False)))
                ids.append(cursor.lastrowid)
            conn.commit()
            return ids

        # 단일 로그
        ts = parse_common_time(raw or {})
        sql = """
            INSERT INTO log_common (log_type, timestamp, raw_log, created_at)
            VALUES (%s, %s, %s, NOW())
        """
        cursor.execute(sql, (log_type, ts, json.dumps(raw, ensure_ascii=False)))
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()



# 온프레 로그 저장 (단일/배열 지원)
def insert_log_onprem(log_ids, data_or_list):
    conn = get_connection()
    cursor = conn.cursor()

    def parse_time(t):
        if not t:
            raise ValueError("시간 필드가 없습니다.")
        try:
            if "T" in t:
                return datetime.fromisoformat(t.replace("Z", "+00:00"))
            else:
                return datetime.strptime(f"2025 {t}", "%Y %b %d %H:%M:%S")
        except Exception:
            return datetime.utcnow()

    def insert_one(log_id, data):
        ts = parse_time(data.get("readable_time") or data.get("time"))
        sql = """
            INSERT INTO log_onprem
            (log_id, host, program,
             in_iface, out_iface, mac, source_ip, destination_ip,
             length, tos, precedence, ttl, packet_id,
             protocol, source_port, destination_port,
             timestamp)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        cursor.execute(
            sql,
            (
                log_id,
                data.get("host"),
                data.get("program"),
                data.get("IN"),
                data.get("OUT"),
                data.get("MAC"),
                data.get("SRC"),
                data.get("DST"),
                int(data.get("LEN")) if data.get("LEN") else None,
                data.get("TOS"),
                data.get("PREC"),
                int(data.get("TTL")) if data.get("TTL") else None,
                int(data.get("ID")) if data.get("ID") else None,
                data.get("PROTO"),
                int(data.get("SPT")) if data.get("SPT") else None,
                int(data.get("DPT")) if data.get("DPT") else None,
                ts,
            ),
        )

    try:
        if isinstance(data_or_list, list):
            for idx, d in enumerate(data_or_list):
                current_id = log_ids[idx] if isinstance(log_ids, list) else log_ids
                insert_one(current_id, d)
        else:
            insert_one(log_ids, data_or_list)
        conn.commit()
    finally:
        cursor.close()
        conn.close()


# 클라우드 로그 저장 (단일/배열 지원)
def insert_log_cloud(log_ids, items):
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
        INSERT INTO log_cloud
        (log_id, version, account_id, interface_id, source_ip, destination_ip,
         protocol, source_port, destination_port, packet, byte,
         start_time, end_time, action, log_status)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                FROM_UNIXTIME(%s), FROM_UNIXTIME(%s), %s, %s)
    """

    try:
        if isinstance(items, list):
            for idx, item in enumerate(items):
                log_id = log_ids[idx] if isinstance(log_ids, list) else log_ids
                cursor.execute(
                    sql,
                    (
                        log_id,
                        item["version"],
                        item["account-id"],
                        item["interface-id"],
                        item["srcaddr"],
                        item["dstaddr"],
                        str(item["protocol"]),
                        item.get("srcport"),
                        item.get("dstport"),
                        item.get("packets"),
                        item.get("bytes"),
                        item.get("start"),
                        item.get("end"),
                        item.get("action"),
                        item.get("log-status"),
                    ),
                )
            conn.commit()
            return

        # 단일
        item = items
        cursor.execute(
            sql,
            (
                log_ids,
                item["version"],
                item["account-id"],
                item["interface-id"],
                item["srcaddr"],
                item["dstaddr"],
                str(item["protocol"]),
                item.get("srcport"),
                item.get("dstport"),
                item.get("packets"),
                item.get("bytes"),
                item.get("start"),
                item.get("end"),
                item.get("action"),
                item.get("log-status"),
            ),
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()
