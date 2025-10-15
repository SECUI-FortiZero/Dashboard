#!/bin/bash
cd /home/fortizero/Dashboard/backend
export $(grep -v '^#' .env | xargs)
PATH=/usr/bin:/bin

TODAY_DIR="/var/log/cloudtrail-logs/$(date +%Y/%m/%d)/"
mkdir -p "$TODAY_DIR"

S3_PREFIX="AWSLogs/401448503579/CloudTrail/ap-northeast-2/$(date +%Y/%m/%d)/"

aws s3 sync \
  "s3://fz-logbucket/$S3_PREFIX" \
  "$TODAY_DIR" \
  --region ap-northeast-2

python3 app/save_cloudtrail.py "$TODAY_DIR" >> /var/log/cloudtrail-logs/cron.log 2>&1
