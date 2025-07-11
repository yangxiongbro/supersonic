#!/bin/bash

#source /opt/pandas-ai/.env.deploy.sh
#nohup python /opt/pandas-ai/apiserver.py > /var/log/pandas-ai.log 2>&1 &
#sleep 30s
#nohup /opt/trino-server/bin/launcher run > /dev/null 2>&1 &
#sleep 60s
#nohup /opt/launchers-standalone-0.9.10/bin/supersonic-daemon.sh restart standalone mysql > /dev/null 2>&1 &
#
#tail -f /dev/null

source /opt/pandas-ai/.env.deploy.sh
nohup python /opt/pandas-ai/apiserver.py > /var/log/pandas-ai.log 2>&1 &
sleep 30s
nohup /opt/trino/bin/launcher run > /var/log/trino.log 2>&1 &
sleep 60s
nohup /opt/launchers-standalone-0.9.10/bin/supersonic-daemon.sh restart standalone mysql > /var/log/supersonic.log 2>&1 &

tail -f /var/log/pandas-ai.log