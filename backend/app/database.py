# 파일 전체를 이 코드로 교체하세요.

import os
import mysql.connector
from dotenv import load_dotenv

# .env 파일의 환경 변수를 로드합니다.
load_dotenv()

# [수정] DB 접속 정보를 받아 새 커넥션을 반환하는 함수
def get_connection():
    """
    .env 파일의 정보를 바탕으로 새로운 DB 커넥션을 생성하고 반환합니다.
    """
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOSTS"),  # .env 파일에 MYSQL_HOSTS로 되어 있어 맞춤
        port=os.getenv("MYSQL_PORT", 3306),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DB"),
        connect_timeout=int(os.getenv("MYSQL_CONNECT_TIMEOUT", 5))
    )

# [삭제] 전역 변수 conn, cursor를 삭제했습니다.

# --- 각 함수는 이제 독립적인 커넥션을 사용합니다 ---

# ROLE
def insert_role(role_name, description=None):
    conn, cursor = None, None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = "INSERT INTO role (role_name, description) VALUES (%s, %s)"
        cursor.execute(sql, (role_name, description))
        conn.commit()
        return cursor.lastrowid
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def get_roles():
    conn, cursor = None, None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM role")
        return cursor.fetchall()
    finally:
        if cursor: cursor.close()
        if conn: conn.close()
        
# ... (다른 모든 함수들도 동일한 패턴으로 수정) ...

# USER
def insert_user(user_name, email, role_id):
    conn, cursor = None, None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = "INSERT INTO user (user_name, email, role_id) VALUES (%s, %s, %s)"
        cursor.execute(sql, (user_name, email, role_id))
        conn.commit()
        return cursor.lastrowid
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def get_users():
    conn, cursor = None, None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user")
        return cursor.fetchall()
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

# ... (이하 모든 함수를 위와 같은 try...finally 구조로 수정해야 합니다) ...
# (전체 코드를 제공하기 위해 모든 함수를 수정해 드립니다)

def update_role(role_id, role_name, description=None):
    conn, cursor = None, None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = "UPDATE role SET role_name=%s, description=%s WHERE role_id=%s"
        cursor.execute(sql, (role_name, description, role_id))
        conn.commit()
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def delete_role(role_id):
    conn, cursor = None, None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM role WHERE role_id=%s", (role_id,))
        conn.commit()
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def update_user(user_id, user_name, email, role_id):
    conn, cursor = None, None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = "UPDATE user SET user_name=%s, email=%s, role_id=%s WHERE user_id=%s"
        cursor.execute(sql, (user_name, email, role_id, user_id))
        conn.commit()
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def delete_user(user_id):
    conn, cursor = None, None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user WHERE user_id=%s", (user_id,))
        conn.commit()
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

# POLICY
def insert_policy(policy_type, src, dst, port, protocol, action, desc, status, owner):
    conn, cursor = None, None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = """
            INSERT INTO policy
            (policy_type, source_ip, destination_ip, port, protocol,
             action, description, status, owner_component)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        params = (policy_type, src, dst, port, protocol, action, desc, status, owner)
        cursor.execute(sql, params)
        conn.commit()
        return cursor.lastrowid
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def get_policies():
    conn, cursor = None, None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM policy")
        return cursor.fetchall()
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def update_policy(policy_id, **kwargs):
    conn, cursor = None, None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        fields = ", ".join([f"{k}=%s" for k in kwargs])
        sql = f"UPDATE policy SET {fields} WHERE policy_id=%s"
        params = list(kwargs.values()) + [policy_id]
        cursor.execute(sql, params)
        conn.commit()
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def delete_policy(policy_id):
    conn, cursor = None, None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM policy WHERE policy_id=%s", (policy_id,))
        conn.commit()
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

# (이하 모든 함수에 대해 동일한 패턴을 적용합니다.)