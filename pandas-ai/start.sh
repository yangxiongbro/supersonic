#!/bin/bash

source .env.deploy.sh
nohup python apiserver.py  > /var/log/pandas-ai.log 2>&1 &

tail -f /dev/null