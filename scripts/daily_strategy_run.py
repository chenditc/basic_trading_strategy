#!/usr/bin/env python3
from datetime import date
import json
import time
import logging
from pathlib import Path

from vnpy.trader.setting import SETTINGS
from vnpy.trader.database import get_database
from opencensus.ext.azure.log_exporter import AzureLogHandler

from asset_management.models import PositionHistory, CurrentPosition, TargetPosition, StrategyRunStatus
from spiders import SpiderStrategyBackTestingWrapper
from spread_rolling import SpreadRollingStrategyBackTestingWrapper
from market_data.data_definition import *
from utils.system_configs import azure_log_key, vnpy_config
from utils.email_util import send_notification

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(AzureLogHandler(
    connection_string=azure_log_key)
)

strategies_to_run = [
    #SpiderStrategyBackTestingWrapper(if_daily_tick_data, if_holding_data),
    SpreadRollingStrategyBackTestingWrapper(future_data=ic_daily_tick_data,
                                            underlying_data=ic_index_data),
    SpreadRollingStrategyBackTestingWrapper(future_data=if_daily_tick_data,
                                            underlying_data=if_index_data)
]

def init_database():
    db = get_database().db
    db.create_tables([PositionHistory, CurrentPosition, TargetPosition, StrategyRunStatus])    

def calculate_target_trade():
    # Current position
    all_current_position = CurrentPosition.select()
    current_symbol_map = {x.symbol: x for x in all_current_position}
    
    all_target_position = TargetPosition.select()
    target_symbol_map = {x.symbol: x for x in all_target_position}
    
    trade_map = {}
    for pos in (set(current_symbol_map.keys()) | set(target_symbol_map.keys())):
        target_pos = 0
        current_pos = 0
        if target_symbol_map.get(pos):
            target_pos = target_symbol_map.get(pos).volume
        if current_symbol_map.get(pos):
            current_pos = current_symbol_map.get(pos).volume
        pos_diff = target_pos - current_pos
        if pos_diff == 0:
            continue
        trade_map[pos] = pos_diff
        
    return trade_map

def daily_strategy_run():
    init_database()
    
    today = date.today()
    
    start_time = time.time()
    
    for strategy in strategies_to_run:
        run_record = StrategyRunStatus.create(strategy = strategy.get_strategy_name(),
                                              status = "started",
                                              reason = "",
                                              run_time = 0,
                                              run_date = today)
        try:
            # Simulate strategy
            strategy.download_data()
            strategy.back_test_and_get_today_target_pos(start_date=datetime(2019,1,1))

            # Get next target position
            last_pos_date = strategy.get_latest_pos_date()
            last_target_pos = strategy.get_latest_pos()
            strategy_name = strategy.get_strategy_name()
            
            reasoning_message = strategy.get_latest_pos_reasoning()
            trade_message = strategy.get_latest_trade_message()

            # Update target position
            deleted_num = TargetPosition.delete().where(TargetPosition.strategy==strategy_name).execute()
            for symbol, volume in last_target_pos.items():
                exchange = symbol.split(".")[-1]
                TargetPosition.create(symbol=symbol,
                                      exchange=exchange,
                                      volume=volume,
                                      strategy=strategy_name,
                                      generate_date=today)
                
            message_body = f"{strategy_name}\n trade:{trade_message}\n{reasoning_message}"
            logger.info(message_body)
            
            if trade_message != "":
                send_notification(str(last_pos_date), message_body)
                
            # Save run record
            run_record.status = "Success"
            run_record.reason = strategy.get_latest_pos_reasoning()
            run_record.run_time = int(time.time() - start_time)
            run_record.save()
        except Exception as e:
            logger.error(e)
            run_record.status = "Failed"
            run_record.reason = str(e)
            run_record.run_time = int(time.time() - start_time)
            run_record.save()
       
if __name__ == "__main__":
    daily_strategy_run()
