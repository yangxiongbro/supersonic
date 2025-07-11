#!/bin/bash

cp -r /opt/app/site-packages/* /usr/local/lib/python3.11/site-packages/

source /opt/app/pandas-ai/.env.deploy.sh
nohup python /opt/app/pandas-ai/apiserver.py > /opt/app/log/pandas-ai.log 2>&1 &
sleep 30s
nohup /opt/app/trino-server/bin/launcher run > /opt/app/log/trino-server.log 2>&1 &
sleep 60s
nohup /opt/app/supersonic/bin/supersonic-daemon.sh restart standalone mysql > /opt/app/log/supersonic.log 2>&1 &

tail -f /opt/app/log/pandas-ai.log