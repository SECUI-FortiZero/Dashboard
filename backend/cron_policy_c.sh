#!/bin/bash
cd /home/fortizero/Dashboard/backend/app
export $(grep -v '^#' ../.env | xargs)
PATH=/usr/bin:/bin

python3 fetch_policies.py >> /var/log/fetch_policies.log 2>&1
