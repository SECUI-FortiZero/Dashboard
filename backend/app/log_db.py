# log_db.py
import json
from datetime import datetime
from database import conn, cursor


# 공통 로그 저장 (단일/배열 지원)
def insert_log_common(log_type: str, ts_or_list, raw=None):
    """
    - 단일 로그: ts_or_list = timestamp, raw = dict
    - 여러 개: ts_or_list = list[dict], raw=None
    """
    ids = []

    if isinstance(ts_or_list, list):  # 여러 개
        for item in ts_or_list:
            ts = item.get("timestamp") or datetime.utcnow().isoformat()
            timestamp = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            sql = """
                INSERT INTO log_common (log_type, timestamp, raw_log, created_at)
                VALUES (%s, %s, %s, NOW())
            """
            cursor.execute(sql, (log_type, timestamp, json.dumps(item, ensure_ascii=False)))
            conn.commit()
            ids.append(cursor.lastrowid)
        return ids

    # 단일
    ts = datetime.fromisoformat(ts_or_list.replace("Z", "+00:00"))
    sql = """
        INSERT INTO log_common (log_type, timestamp, raw_log, created_at)
        VALUES (%s, %s, %s, NOW())
    """
    cursor.execute(sql, (log_type, ts, json.dumps(raw, ensure_ascii=False)))
    conn.commit()
    return cursor.lastrowid


# 온프레 로그 저장 (단일/배열 지원)
def insert_log_onprem(log_ids, data_or_list):
    """
    log_ids : int 또는 list[int]
    data_or_list : dict 또는 list[dict]
    """
    if isinstance(data_or_list, list):
        for idx, data in enumerate(data_or_list):
            log_id = log_ids[idx] if isinstance(log_ids, list) else log_ids
            d = data.get("details", {})
            ts = datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
            sql = """
                INSERT INTO log_onprem
                (log_id, host, in_iface, out_iface, source_ip, destination_ip,
                 protocol, source_port, destination_port, action, timestamp)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """
            cursor.execute(sql, (
                log_id,
                data.get("host"),
                d.get("in_iface"),
                d.get("out_iface"),
                d.get("src_ip"),
                d.get("dst_ip"),
                d.get("proto"),
                d.get("src_port"),
                d.get("dst_port"),
                d.get("action"),
                ts
            ))
            conn.commit()
        return

    # 단일
    d = data_or_list.get("details", {})
    ts = datetime.fromisoformat(data_or_list["timestamp"].replace("Z", "+00:00"))
    sql = """
        INSERT INTO log_onprem
        (log_id, host, in_iface, out_iface, source_ip, destination_ip,
         protocol, source_port, destination_port, action, timestamp)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """
    cursor.execute(sql, (
        log_ids,
        data_or_list.get("host"),
        d.get("in_iface"),
        d.get("out_iface"),
        d.get("src_ip"),
        d.get("dst_ip"),
        d.get("proto"),
        d.get("src_port"),
        d.get("dst_port"),
        d.get("action"),
        ts
    ))
    conn.commit()


# 클라우드 로그 저장 (단일/배열 지원)
def insert_log_cloud(log_ids, items):
    """
    log_ids : int 또는 list[int]
    items : dict 또는 list[dict]
    """
    if isinstance(items, list):
        for idx, item in enumerate(items):
            log_id = log_ids[idx] if isinstance(log_ids, list) else log_ids
            sql = """
                INSERT INTO log_cloud
                (log_id, version, account_id, interface_id, source_ip, destination_ip,
                 protocol, source_port, destination_port, packet, byte,
                 start_time, end_time, action, log_status)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                        FROM_UNIXTIME(%s), FROM_UNIXTIME(%s), %s, %s)
            """
            cursor.execute(sql, (
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
                item.get("log-status")
            ))
            conn.commit()
        return

    # 단일
    item = items
    sql = """
        INSERT INTO log_cloud
        (log_id, version, account_id, interface_id, source_ip, destination_ip,
         protocol, source_port, destination_port, packet, byte,
         start_time, end_time, action, log_status)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                FROM_UNIXTIME(%s), FROM_UNIXTIME(%s), %s, %s)
    """
    cursor.execute(sql, (
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
        item.get("log-status")
    ))
    conn.commit()
