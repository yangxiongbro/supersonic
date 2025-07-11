#!/usr/bin/env bash

#### Set below DB configs to connect to your own database
# Supported DB_TYPE:  h2, mysql, postgres
export S2_DB_TYPE=mysql
export S2_DB_HOST=192.168.16.100
export S2_DB_PORT=3306
export S2_DB_USER=root
export S2_DB_PASSWORD=root
export S2_DB_DATABASE=mutil_agent_supersonic

export SYNC_DATA_WHEN_START_UP=true

# 单独部署
#export TRINO_HOST=192.168.16.10
#export TRINO_PORT=31744
#export TRINO_USER=demo
#export TRINO_PASSWORD=
#
#export PANDAS_AI_HOST=192.168.16.10
#export PANDAS_AI_PORT=32701

# 集成部署部署
export TRINO_HOST=127.0.0.1
export TRINO_PORT=18080
export TRINO_USER=demo
export TRINO_PASSWORD=

export PANDAS_AI_HOST=127.0.0.1
export PANDAS_AI_PORT=8081
