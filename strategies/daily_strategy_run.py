from datetime import date
import time

from vnpy.trader.database import get_database

from asset_management.models import PositionHistory, CurrentPosition, TargetPosition, StrategyRunStatus
from spiders import SpiderStrategyBackTestingWrapper
from spread_rolling import SpreadRollingStrategyBackTestingWrapper
from market_data.data_definition import *

strategies_to_run = [
    SpiderStrategyBackTestingWrapper(if_daily_tick_data, if_holding_data),
    SpreadRollingStrategyBackTestingWrapper(future_data=ic_daily_tick_data,
                                            underlying_data=ic_index_data),
    SpreadRollingStrategyBackTestingWrapper(future_data=if_daily_tick_data,
                                            underlying_data=if_index_data)
]

def init_database():
    db = get_database().db
    db.create_tables([PositionHistory, CurrentPosition, TargetPosition, StrategyRunStatus])    

def calculate_target_trade():
    pass
    
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

            # Update target position
            deleted_num = TargetPosition.delete().where(TargetPosition.strategy==strategy_name).execute()
            for symbol, volume in last_target_pos.items():
                exchange = symbol.split(".")[-1]
                TargetPosition.create(symbol=symbol,
                                      exchange=exchange,
                                      volume=volume,
                                      strategy=strategy_name,
                                      generate_date=today)
                
            # Save run record
            run_record.status = "Success"
            run_record.reason = strategy.get_latest_pos_reasoning()
            run_record.run_time = int(time.time() - start_time)
            run_record.save()
        except Exception as e:
            run_record.status = "Failed"
            run_record.reason = str(e)
            run_record.run_time = int(time.time() - start_time)
            run_record.save()
        
    calculate_target_trade()