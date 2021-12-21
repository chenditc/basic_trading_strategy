#!/usr/bin/env python3
from datetime import date
import json
import logging

from opencensus.ext.azure.log_exporter import AzureLogHandler
from vnpy.trader.database import get_database

from asset_management.models import PositionHistory, CurrentPosition, TargetPosition, StrategyRunStatus
from utils.system_configs import azure_log_key
from asset_management import asset_net_value
from utils.tencent_db_init import connect_db_and_wait

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(AzureLogHandler(
    connection_string=azure_log_key)
)

def init_database():
    connect_db_and_wait()
    db = get_database().db
    db.create_tables([PositionHistory, CurrentPosition, TargetPosition, StrategyRunStatus])    
    
    
if __name__ == "__main__":
    init_database()
    asset_net_value.calculate_latest_position_history()
    