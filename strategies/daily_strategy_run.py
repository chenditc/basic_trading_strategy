from datetime import date

from vnpy.trader.database import get_database

from asset_management.models import PositionHistory, CurrentPosition, TargetPosition
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
    db.create_tables([PositionHistory, CurrentPosition, TargetPosition])    

def daily_strategy_run():
    init_database()
    
    today = date.today()
    for strategy in strategies_to_run:
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
        
        