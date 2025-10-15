import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    """
    MYSQL_HOSTS에 여러 호스트를 콤마(,)로 나열하면 순서대로 접속 시도.
    예: MYSQL_HOSTS=192.168.5.30,127.0.0.1
    """
    hosts_env = os.getenv("MYSQL_HOSTS") or os.getenv("MYSQL_HOST", "127.0.0.1")
    hosts = [h.strip() for h in hosts_env.split(",") if h.strip()]
    port = int(os.getenv("MYSQL_PORT", "3306"))
    user = os.getenv("MYSQL_USER")
    password = os.getenv("MYSQL_PASSWORD")
    database = os.getenv("MYSQL_DB")
    timeout = int(os.getenv("MYSQL_CONNECT_TIMEOUT", "5"))

    last_err = None

    for host in hosts:
        try:
            return mysql.connector.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database,
                connection_timeout=timeout,
            )
        except Exception as e:
            last_err = e
            continue

    # 모든 시도가 실패하면 마지막 에러를 발생시킴
    raise last_err or RuntimeError("No available MySQL hosts")
