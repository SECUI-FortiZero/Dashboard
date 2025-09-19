#!/bin/bash
cd /home/fortizero/Dashboard/backend
export $(grep -v '^#' .env | xargs)
PATH=/usr/bin:/bin

TODAY_DIR="/var/log/s3-logs/$(date +%Y/%m/%d)/"

aws s3 sync s3://fz-logbucket/AWSLogs/401448503579/vpcflowlogs/ap-northeast-2/$(date +%Y/%m/%d)/ "$TODAY_DIR" --region ap-northeast-2

#python3 app/save_log.py "$TODAY_DIR" >> /var/log/s3-logs/cron.log 2>&1