from vnpy.trader.object import BarData
from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.database import get_database

import akshare as ak
from pytz import timezone

from datetime import datetime, timedelta, date

CHINA_TZ = timezone("Asia/Shanghai")
UTC_TZ = timezone("UTC")

class AbstractDataProvider():
    def __init__(self, database_manager=None):
        self.database_manager = database_manager
        if self.database_manager is None:
            self.database_manager = get_database()
        self.download_step_days = 30
        
        self.trade_calendar_list = None
        
    def get_latest_date_for_symbol(self, symbol, data_requirement):
        bar_list = self.database_manager.load_bar_data(symbol=symbol, 
                                                      exchange=data_requirement.exchange, 
                                                      interval=data_requirement.interval, 
                                                      start=datetime.strptime("19000101", '%Y%m%d'), 
                                                      end=datetime.strptime("20550101", '%Y%m%d'))
        if len(bar_list) == 0:
            return
        return bar_list[-1].datetime.date()
