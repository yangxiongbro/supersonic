#!/bin/bash

nohup /opt/app/launchers-standalone-0.9.10/bin/supersonic-daemon.sh restart standalone mysql  > /var/log/supersonic.log 2>&1 &

tail -f /dev/null