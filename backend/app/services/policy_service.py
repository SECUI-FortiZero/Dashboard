from datetime import datetime
import json
from app.connector_db import get_connection
import json


from app.connector_db import get_connection

def get_policy_cloud(range_type):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    if range_type == "daily":
        sql = """
        SELECT raw_event
        FROM policy_history_c
        WHERE timestamp >= NOW() - INTERVAL 1 DAY
        ORDER BY timestamp DESC
        """
    elif range_type == "weekly":
        sql = """
        SELECT raw_event
        FROM policy_history_c
        WHERE timestamp >= NOW() - INTERVAL 7 DAY
        ORDER BY timestamp DESC
        """
    elif range_type == "monthly":
        sql = """
        SELECT raw_event
        FROM policy_history_c
        WHERE timestamp >= NOW() - INTERVAL 1 MONTH
        ORDER BY timestamp DESC
        """
    elif range_type == "hour":
        sql = """
        SELECT raw_event
        FROM policy_history_c
        WHERE timestamp >= NOW() - INTERVAL 1 HOUR
        ORDER BY timestamp DESC
        """
    elif range_type == "10min":
        sql = """
        SELECT raw_event
        FROM policy_history_c
        WHERE timestamp >= NOW() - INTERVAL 10 MINUTE
        ORDER BY timestamp DESC
        """
    else:
        raise ValueError("Invalid range type")

    cur.execute(sql)
    rows = cur.fetchall()

    cur.close()
    conn.close()
    return rows


def get_policy_onprem(range_type):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    if range_type == "daily":
        sql = """
        SELECT message
        FROM policy_history_o
        WHERE timestamp >= NOW() - INTERVAL 1 DAY
        ORDER BY timestamp DESC
        """
    elif range_type == "weekly":
        sql = """
        SELECT message
        FROM policy_history_o
        WHERE timestamp >= NOW() - INTERVAL 7 DAY
        ORDER BY timestamp DESC
        """
    elif range_type == "monthly":
        sql = """
        SELECT message
        FROM policy_history_o
        WHERE timestamp >= NOW() - INTERVAL 1 MONTH
        ORDER BY timestamp DESC
        """
    elif range_type == "hour":
        sql = """
        SELECT message
        FROM policy_history_o
        WHERE timestamp >= NOW() - INTERVAL 1 HOUR
        ORDER BY timestamp DESC
        """
    elif range_type == "10min":
        sql = """
        SELECT message
        FROM policy_history_o
        WHERE timestamp >= NOW() - INTERVAL 10 MINUTE
        ORDER BY timestamp DESC
        """
    else:
        raise ValueError("Invalid range type")

    cur.execute(sql)
    rows = cur.fetchall()

    cur.close()
    conn.close()
    return rows