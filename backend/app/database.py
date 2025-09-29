# app/database.py  (MySQL only / no globals)
import json
from datetime import datetime
from typing import Any, Optional, Tuple

from app.connector_db import get_connection

# --- 내부 유틸 ---

def _fetch_all(query: str, params: Optional[Tuple[Any, ...]] = None):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(query, params or ())
        rows = cur.fetchall()
        return rows
    finally:
        cur.close()
        conn.close()

def _execute_commit(query: str, params: Optional[Tuple[Any, ...]] = None) -> int:
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(query, params or ())
        conn.commit()
        return cur.lastrowid or 0
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

# --- ROLE ---

def insert_role(role_name: str, description: Optional[str] = None) -> int:
    sql = "INSERT INTO role (role_name, description) VALUES (%s, %s)"
    return _execute_commit(sql, (role_name, description))

def get_roles():
    return _fetch_all("SELECT * FROM role")

def update_role(role_id: int, role_name: str, description: Optional[str] = None) -> None:
    sql = "UPDATE role SET role_name=%s, description=%s WHERE role_id=%s"
    _execute_commit(sql, (role_name, description, role_id))

def delete_role(role_id: int) -> None:
    _execute_commit("DELETE FROM role WHERE role_id=%s", (role_id,))

# --- USER ---

def insert_user(user_name: str, email: str, role_id: int) -> int:
    sql = "INSERT INTO user (user_name, email, role_id) VALUES (%s, %s, %s)"
    return _execute_commit(sql, (user_name, email, role_id))

def get_users():
    return _fetch_all("SELECT * FROM user")

def update_user(user_id: int, user_name: str, email: str, role_id: int) -> None:
    sql = "UPDATE user SET user_name=%s, email=%s, role_id=%s WHERE user_id=%s"
    _execute_commit(sql, (user_name, email, role_id, user_id))

def delete_user(user_id: int) -> None:
    _execute_commit("DELETE FROM user WHERE user_id=%s", (user_id,))

# --- POLICY ---

def insert_policy(policy_type: str, src: str, dst: str, port: str, protocol: str,
                  action: str, desc: Optional[str], status: str, owner: str) -> int:
    sql = """
        INSERT INTO policy
        (policy_type, source_ip, destination_ip, port, protocol,
         action, description, status, owner_component)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """
    return _execute_commit(sql, (policy_type, src, dst, port, protocol,
                                 action, desc, status, owner))

def get_policies():
    return _fetch_all("SELECT * FROM policy")

def update_policy(policy_id: int, **kwargs) -> None:
    if not kwargs:
        return
    fields = ", ".join([f"{k}=%s" for k in kwargs.keys()])
    sql = f"UPDATE policy SET {fields} WHERE policy_id=%s"
    params = tuple(kwargs.values()) + (policy_id,)
    _execute_commit(sql, params)

def delete_policy(policy_id: int) -> None:
    _execute_commit("DELETE FROM policy WHERE policy_id=%s", (policy_id,))

# --- POLICY HISTORY ---

def insert_policy_history(policy_id: int, user_id: int, change_type: str,
                          before_change: Any, after_change: Any,
                          reason: Optional[str] = None) -> int:
    sql = """
        INSERT INTO policy_history
        (policy_id, user_id, change_type, before_change, after_change, reason)
        VALUES (%s,%s,%s,%s,%s,%s)
    """
    before_s = json.dumps(before_change, ensure_ascii=False) if not isinstance(before_change, str) else before_change
    after_s  = json.dumps(after_change,  ensure_ascii=False) if not isinstance(after_change, str)  else after_change
    return _execute_commit(sql, (policy_id, user_id, change_type, before_s, after_s, reason))

def get_policy_history():
    return _fetch_all("SELECT * FROM policy_history")

# --- SESSION ---

def insert_session(user_id: int, source_ip: str, target_server: str, start_time: datetime,
                   end_time: Optional[datetime] = None, commands: Optional[str] = None) -> int:
    sql = """
        INSERT INTO session
        (user_id, source_ip, target_server, start_time, end_time, commands)
        VALUES (%s,%s,%s,%s,%s,%s)
    """
    return _execute_commit(sql, (user_id, source_ip, target_server, start_time, end_time, commands))

def get_sessions():
    return _fetch_all("SELECT * FROM session")

# --- ALERT ---

def insert_alert(alert_type: str, severity: str, related_log_ids: Optional[Any] = None,
                 details: Optional[Any] = None, status: str = "Pending") -> int:
    sql = """
        INSERT INTO alert
        (alert_type, severity, related_log_ids, details, status)
        VALUES (%s,%s,%s,%s,%s)
    """
    r_json = json.dumps(related_log_ids, ensure_ascii=False) if (related_log_ids is not None and not isinstance(related_log_ids, str)) else related_log_ids
    d_json = json.dumps(details,         ensure_ascii=False) if (details is not None and not isinstance(details, str)) else details
    return _execute_commit(sql, (alert_type, severity, r_json, d_json, status))

def get_alerts():
    return _fetch_all("SELECT * FROM alert")

# --- REPORT ---

def insert_report(report_type: str, start_date: datetime, end_date: datetime, file_path: str) -> int:
    sql = """
        INSERT INTO report
        (report_type, start_date, end_date, file_path)
        VALUES (%s,%s,%s,%s)
    """
    return _execute_commit(sql, (report_type, start_date, end_date, file_path))

def get_reports():
    return _fetch_all("SELECT * FROM report")

# --- LOG ---

def get_log_common(limit: int = 100):
    return _fetch_all("SELECT * FROM log_common ORDER BY created_at DESC LIMIT %s", (limit,))

def get_log_onprem(log_id: int):
    return _fetch_all("SELECT * FROM log_onprem WHERE log_id=%s", (log_id,))

def get_log_cloud(log_id: int):
    return _fetch_all("SELECT * FROM log_cloud WHERE log_id=%s", (log_id,))
