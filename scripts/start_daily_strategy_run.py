#!/bin/bash
set -e
set -x
#mkdir -p /root/.vntrader/
#echo "{\"database.name\" : \"$DATABASE_NAME\",\"database.database\" : \"$DATABASE_DATABASE\",\"database.user\" : \"$DATABASE_USER\",\"database.password\": \"$DATABASE_PASSWORD\",\"database.host\": \"$DATABASE_HOST\",\"database.port\" : $DATABASE_PORT}" > /root/.vntrader/vt_setting.json
python3 $(dirname "$0")/daily_strategy_run.py 
