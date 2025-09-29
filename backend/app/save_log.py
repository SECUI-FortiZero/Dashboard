import os, sys, json, gzip, mysql.connector
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

load_dotenv()
kst = timezone(timedelta(hours=9))

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DB"),
    )

def insert_log_common(cur, log_type, raw, timestamp):
    sql = """INSERT INTO log_common (log_type, timestamp, raw_log, created_at)
             VALUES (%s, %s, %s, NOW())"""
    cur.execute(sql, (log_type, timestamp, json.dumps(raw, ensure_ascii=False)))
    return cur.lastrowid

def insert_log_cloud(cur, log_id, entry):
    sql = """INSERT IGNORE INTO log_cloud
             (log_id, version, account_id, interface_id, source_ip, destination_ip,
              protocol, source_port, destination_port, packet, byte,
              start_time, end_time, action, log_status)
             VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""

    def to_dt(epoch):
        if not epoch:
            return None
        try:
            e = int(epoch)
            if e > 10**12:
                e //= 1000
            return datetime.fromtimestamp(e, tz=timezone.utc).astimezone(kst).replace(tzinfo=None)
        except Exception:
            return None

    cur.execute(sql, (
        log_id,
        int(entry.get("version")),
        entry.get("account-id"),
        entry.get("interface-id"),
        entry.get("srcaddr"),
        entry.get("dstaddr"),
        str(entry.get("protocol")),
        int(entry.get("srcport")) if entry.get("srcport") else None,
        int(entry.get("dstport")) if entry.get("dstport") else None,
        entry.get("packets"),
        entry.get("bytes"),
        to_dt(entry.get("start")),
        to_dt(entry.get("end")),
        entry.get("action"),
        entry.get("log-status"),
    ))

def process_file(path, cur):
    opener = gzip.open if path.endswith(".gz") else open
    with opener(path, "rt", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("version"):
                continue
            try:
                parts = line.split()
                if len(parts) < 14:
                    print(f"❌ Invalid VPC log line in {path}: {line}")
                    continue

                entry = {
                    "version": parts[0], "account-id": parts[1], "interface-id": parts[2],
                    "srcaddr": parts[3], "dstaddr": parts[4],
                    "srcport": parts[5], "dstport": parts[6],
                    "protocol": parts[7], "packets": parts[8], "bytes": parts[9],
                    "start": parts[10], "end": parts[11],
                    "action": parts[12], "log-status": parts[13],
                }

                ts = datetime.now(kst).replace(tzinfo=None)
                try:
                    e = int(entry["start"])
                    if e > 10**12:
                        e //= 1000
                    ts = datetime.fromtimestamp(e, tz=timezone.utc).astimezone(kst).replace(tzinfo=None)
                except Exception:
                    pass

                log_id = insert_log_common(cur, "CLOUD", entry, ts)
                insert_log_cloud(cur, log_id, entry)
            except Exception as e:
                print(f"❌ Parse error in {path}: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 save_logs.py <log_directory>")
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
        try: cur.close()
        except: pass
        try: conn.close()
        except: pass

if __name__ == "__main__":
    main()
