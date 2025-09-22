#!/usr/bin/env python3
import os
import sys
import json
import gzip
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

# DB 접속
def get_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DB"),
    )


# 이전 after_change 가져오기
def get_previous_after(cur, policy_id):
    sql = """
        SELECT after_change
        FROM policy_history_c
        WHERE policy_id = %s
        ORDER BY history_id DESC
        LIMIT 1
    """
    cur.execute(sql, (policy_id,))
    row = cur.fetchone()
    return row[0] if row else None


# policy_id 추출
def extract_policy_id(event):
    req = event.get("requestParameters") or {}

    # S3 버킷 정책
    if "bucketName" in req:
        return req["bucketName"]

    # IAM 정책
    if "policyArn" in req:
        return req["policyArn"]
    if "policyName" in req:
        return req["policyName"]

    # EC2 Security Group
    if "groupName" in req:
        return req["groupName"]

    # CloudTrail Trail 이름
    if "name" in req:
        return req["name"]

    return 0

# policy_history_c insert
def insert_policy_history(cur, event, user_id=0):
    event_id = event.get("eventID")
    event_time = event.get("eventTime")
    event_name = event.get("eventName", "")
    read_only = event.get("readOnly", False)

    # 조회 이벤트는 스킵
    if read_only:
        return False

    lower = event_name.lower()
    if not any(x in lower for x in ["create", "put", "update", "delete"]):
        return False

    # policy_id 추출
    policy_id = extract_policy_id(event)

    # 변경 유형
    lower = event_name.lower()

    if lower.startswith("create"):
        change_type = "CREATE"
    elif lower.startswith("delete") or lower.startswith("revoke"):
        change_type = "DELETE"
    elif lower.startswith("put") or lower.startswith("update") or lower.startswith("authorize") or lower.startswith("modify"):
        change_type = "UPDATE"
    else:
        change_type = "UPDATE"


    after_json = json.dumps(event.get("requestParameters") or {}, ensure_ascii=False)
    before_json = get_previous_after(cur, policy_id) if policy_id else None
    raw_event = json.dumps(event, ensure_ascii=False)

    sql = """
    INSERT IGNORE INTO policy_history_c
        (policy_id, user_id, change_type,
         before_change, after_change,
         reason, timestamp, event_id, raw_event)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """
    cur.execute(sql, (
        policy_id,
        user_id,
        change_type,
        before_json,
        after_json,
        None,
        event_time,
        event_id,
        raw_event
    ))
    return True

# 파일 처리
def process_file(path, cur):
    opener = gzip.open if path.endswith(".gz") else open
    with opener(path, "rt", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except Exception as e:
            print(f"❌ JSON 파싱 실패: {path} ({e})")
            return

        records = data.get("Records", [])
        if not records:
            print(f"[INFO] Records 없음: {path}")
            return

        inserted = 0
        for rec in records:
            try:
                if insert_policy_history(cur, rec, user_id=0):
                    inserted += 1
            except Exception as e:
                print(f"❌ {path} 이벤트 저장 오류: {e}")

        if inserted:
            print(f"[OK] {path}: {inserted} rows inserted")
        else:
            print(f"[SKIP] {path}: 변경 이벤트 없음")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 save_cloudtrail.py <log_directory>")
        sys.exit(1)

    log_dir = sys.argv[1]
    if not os.path.isdir(log_dir):
        print(f"❌ Not a directory: {log_dir}")
        sys.exit(1)

    conn = get_connection()
    cur = conn.cursor()

    try:
        for fname in os.listdir(log_dir):
            fpath = os.path.join(log_dir, fname)
            if os.path.isfile(fpath) and (fname.endswith(".json") or fname.endswith(".gz")):
                print(f"Processing {fpath} ...")
                process_file(fpath, cur)
        conn.commit()
    finally:
        try:
            cur.close()
        except:
            pass
        try:
            conn.close()
        except:
            pass

if __name__ == "__main__":
    main()
