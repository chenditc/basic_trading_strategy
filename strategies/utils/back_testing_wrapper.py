from vnpy.trader.database import get_database

from collections import defaultdict
import logging
from datetime import datetime

from market_data.akshare_data_provider import AkShareDataProvider
from market_data.tushare_data_provider import TuShareDataProvider
from market_data.smart_data_provider import SmartDataProvider
from utils.email_util import send_notification
from utils.system_configs import azure_log_key

logger = logging.getLogger(__name__)

if azure_log_key != "":
    from opencensus.ext.azure.log_exporter import AzureLogHandler
    logger.addHandler(AzureLogHandler(
        connection_string=azure_log_key)
    )

class BackTestingWrapper():
    def __init__(self, data_provider=None):
        if data_provider:
            self.data_provider = data_provider
        else:
            self.data_provider = SmartDataProvider()
        
        self.data_provider.update_future_info()
        
        self.rates = defaultdict(lambda:0.000023)
        self.slippages = defaultdict(lambda:0)
        self.sizes = defaultdict(lambda:1)
        self.priceticks = defaultdict(lambda:0.1)
        self.capital = 1_000_000
        
        self.target_pos_map = {}
        self.target_pos_reason = {}
        
        self.engine = None
        
    def get_future_size_for_symbol(self, symbol):
        future_info = self.data_provider.get_future_info_for_symbol(symbol)
        if future_info:
            return defaultdict(lambda:float(future_info.multiplier))
        else:
            return self.sizes
                        
    def get_strategy_name(self):
        return type(self).__name__
                
    def show_result(self):
        df = self.engine.calculate_result()

        self.engine.calculate_statistics()
        self.engine.show_chart()
        return df
        
    def get_latest_pos_date(self):
        return max(self.target_pos_map.keys())
    
    def get_latest_pos(self):
        latest_date = self.get_latest_pos_date()
        return self.target_pos_map[latest_date]
    
    def get_latest_pos_reasoning(self):
        latest_date = self.get_latest_pos_date()
        return self.target_pos_reason[latest_date]
    
    def get_latest_trade_message(self):
        trade_message = ""
        
        last_two_days = sorted(list(self.target_pos_map.keys()))[-2:]
        pos1 = self.target_pos_map[last_two_days[0]]
        pos2 = self.target_pos_map[last_two_days[1]]
        
        for pos in (set(pos1.keys()) | set(pos2.keys())):
            pos_diff = pos2.get(pos, 0) - pos1.get(pos, 0) 
            if pos_diff == 0:
                continue
            if pos_diff > 0:
                trade_message += f"Buy {pos}: {pos_diff}\n"
            else:
                trade_message += f"Sell {pos}: {pos_diff}\n"
        return trade_message
    
    def run_strategy_and_send_trade_message(self, start_date=datetime(2019,1,1)):
        self.download_data()
        self.back_test_and_get_today_target_pos(start_date=start_date)
        
        strategy_name = self.get_strategy_name()
        reasoning_message = self.get_latest_pos_reasoning()
        trade_message = self.get_latest_trade_message()
        
        body = f"{strategy_name}\n trade:{trade_message}\n{reasoning_message}"
        if trade_message == "":
            logger.info(body)
            
        
        logger.info(body)
        send_notification(str(self.get_latest_pos_date()), body)
