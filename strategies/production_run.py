from spread_rolling import SpreadRollingStrategyBackTestingWrapper
from market_data.data_definition import *

prod_strategies = [
    SpreadRollingStrategyBackTestingWrapper(future_data=ic_daily_tick_data, underlying_data=ic_index_data)
]

for strategy in prod_strategies:
    strategy.run_strategy_and_send_trade_message()