#!/usr/bin/env python3
import os
import json
import mysql.connector
from datetime import datetime
from dotenv import load_dotenv
import boto3

load_dotenv()

#DB 접속
def get_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DB"),
    )

#배치 ID 생성
def create_batch(cur):
    cur.execute("INSERT INTO policy_cloud (timestamp) VALUES (NOW())")
    return cur.lastrowid

#S3 정책 저장
def save_s3(cur, batch_id, region):
    s3 = boto3.client("s3", region_name=region)
    buckets = s3.list_buckets().get("Buckets", [])
    for b in buckets:
        name = b["Name"]
        try:
            pol = s3.get_bucket_policy(Bucket=name)["Policy"]
        except s3.exceptions.from_code("NoSuchBucketPolicy"):
            pol = None
        cur.execute(
            """
            INSERT INTO policy_cloud_s3 (policy_id, bucket_name, policy_doc)
            VALUES (%s, %s, %s)
            """,
            (batch_id, name, pol),
        )

#IAM 정책 저장
def save_iam(cur, batch_id, region):
    iam = boto3.client("iam", region_name=region)
    resp = iam.list_policies(Scope="Local")
    for p in resp.get("Policies", []):
        arn = p["Arn"]
        name = p.get("PolicyName")
        ver = p.get("DefaultVersionId")
        doc = None
        if ver:
            v = iam.get_policy_version(PolicyArn=arn, VersionId=ver)
            doc = json.dumps(v["PolicyVersion"]["Document"], ensure_ascii=False)
        cur.execute(
            """
            INSERT INTO policy_cloud_iam
                (policy_id, policy_arn, policy_name, default_version, document)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (batch_id, arn, name, ver, doc),
        )

#SG 정책 저장
def save_sg(cur, batch_id, region):
    ec2 = boto3.client("ec2", region_name=region)
    resp = ec2.describe_security_groups()
    for sg in resp.get("SecurityGroups", []):
        gid = sg["GroupId"]
        gname = sg.get("GroupName")
        desc = sg.get("Description")
        vpc = sg.get("VpcId")
        rules = json.dumps(
            {
                "Ingress": sg.get("IpPermissions"),
                "Egress": sg.get("IpPermissionsEgress"),
            },
            ensure_ascii=False,
        )
        cur.execute(
            """
            INSERT INTO policy_cloud_sg
                (policy_id, group_id, group_name, description, vpc_id, rule)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (batch_id, gid, gname, desc, vpc, rules),
        )


def main():
    region = os.getenv("AWS_DEFAULT_REGION", "ap-northeast-2")
    conn = get_connection()
    cur = conn.cursor()

    try:
        batch_id = create_batch(cur)
        save_s3(cur, batch_id, region)
        save_iam(cur, batch_id, region)
        save_sg(cur, batch_id, region)
        conn.commit()
        print(f"[OK] Snapshot stored (batch_id={batch_id})")
    except Exception as e:
        conn.rollback()
        print(f"❌ Snapshot error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    main()
