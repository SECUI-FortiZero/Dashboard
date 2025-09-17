import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

conn = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database=os.getenv("MYSQL_DB")
)
cursor = conn.cursor(dictionary=True)

#ROLE
def insert_role(role_name, description=None):
    sql = "INSERT INTO role (role_name, description) VALUES (%s, %s)"
    cursor.execute(sql, (role_name, description))
    conn.commit()
    return cursor.lastrowid

def get_roles():
    cursor.execute("SELECT * FROM role")
    return cursor.fetchall()

def update_role(role_id, role_name, description=None):
    sql = "UPDATE role SET role_name=%s, description=%s WHERE role_id=%s"
    cursor.execute(sql, (role_name, description, role_id))
    conn.commit()

def delete_role(role_id):
    cursor.execute("DELETE FROM role WHERE role_id=%s", (role_id,))
    conn.commit()

#USER
def insert_user(user_name, email, role_id):
    sql = "INSERT INTO user (user_name, email, role_id) VALUES (%s, %s, %s)"
    cursor.execute(sql, (user_name, email, role_id))
    conn.commit()
    return cursor.lastrowid

def get_users():
    cursor.execute("SELECT * FROM user")
    return cursor.fetchall()

def update_user(user_id, user_name, email, role_id):
    sql = "UPDATE user SET user_name=%s, email=%s, role_id=%s WHERE user_id=%s"
    cursor.execute(sql, (user_name, email, role_id, user_id))
    conn.commit()

def delete_user(user_id):
    cursor.execute("DELETE FROM user WHERE user_id=%s", (user_id,))
    conn.commit()

#POLICY
def insert_policy(policy_type, src, dst, port, protocol, action, desc, status, owner):
    sql = """
        INSERT INTO policy
        (policy_type, source_ip, destination_ip, port, protocol,
         action, description, status, owner_component)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """
    cursor.execute(sql, (policy_type, src, dst, port, protocol,
                         action, desc, status, owner))
    conn.commit()
    return cursor.lastrowid

def get_policies():
    cursor.execute("SELECT * FROM policy")
    return cursor.fetchall()

def update_policy(policy_id, **kwargs):
    fields = ", ".join([f"{k}=%s" for k in kwargs])
    sql = f"UPDATE policy SET {fields} WHERE policy_id=%s"
    params = list(kwargs.values()) + [policy_id]
    cursor.execute(sql, params)
    conn.commit()

def delete_policy(policy_id):
    cursor.execute("DELETE FROM policy WHERE policy_id=%s", (policy_id,))
    conn.commit()

#POLICY HISTORY
def insert_policy_history(policy_id, user_id, change_type,
                          before_change, after_change, reason=None):
    sql = """
        INSERT INTO policy_history
        (policy_id, user_id, change_type, before_change, after_change, reason)
        VALUES (%s,%s,%s,%s,%s,%s)
    """
    cursor.execute(sql, (policy_id, user_id, change_type,
                         before_change, after_change, reason))
    conn.commit()
    return cursor.lastrowid

def get_policy_history():
    cursor.execute("SELECT * FROM policy_history")
    return cursor.fetchall()

#SESSION
def insert_session(user_id, source_ip, target_server, start_time,
                   end_time=None, commands=None):
    sql = """
        INSERT INTO session
        (user_id, source_ip, target_server, start_time, end_time, commands)
        VALUES (%s,%s,%s,%s,%s,%s)
    """
    cursor.execute(sql, (user_id, source_ip, target_server,
                         start_time, end_time, commands))
    conn.commit()
    return cursor.lastrowid

def get_sessions():
    cursor.execute("SELECT * FROM session")
    return cursor.fetchall()

#LOG
def insert_log(src_ip, dst_ip, src_port, dst_port, protocol,
               action, log_source, raw_log):
    sql = """
        INSERT INTO log
        (source_ip, destination_ip, source_port, destination_port,
         protocol, action, log_source, raw_log)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """
    cursor.execute(sql, (src_ip, dst_ip, src_port, dst_port,
                         protocol, action, log_source, raw_log))
    conn.commit()
    return cursor.lastrowid

def get_logs():
    cursor.execute("SELECT * FROM log")
    return cursor.fetchall()

#ALERT
def insert_alert(alert_type, severity, related_log_ids=None,
                 details=None, status="Pending"):
    sql = """
        INSERT INTO alert
        (alert_type, severity, related_log_ids, details, status)
        VALUES (%s,%s,%s,%s,%s)
    """
    cursor.execute(sql, (alert_type, severity, related_log_ids,
                         details, status))
    conn.commit()
    return cursor.lastrowid

def get_alerts():
    cursor.execute("SELECT * FROM alert")
    return cursor.fetchall()

#REPORT
def insert_report(report_type, start_date, end_date, file_path):
    sql = """
        INSERT INTO report
        (report_type, start_date, end_date, file_path)
        VALUES (%s,%s,%s,%s)
    """
    cursor.execute(sql, (report_type, start_date, end_date, file_path))
    conn.commit()
    return cursor.lastrowid

def get_reports():
    cursor.execute("SELECT * FROM report")
    return cursor.fetchall()


def close_connection():
    cursor.close()
    conn.close()
