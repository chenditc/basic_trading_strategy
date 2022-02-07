from datetime import datetime, timedelta, date

from vnpy.trader.object import BarData
from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.database import get_database
import tushare as ts
from pytz import timezone
import pandas as pd
import numpy as np
import peewee
import logging

from utils.system_configs import tushare_config
from market_data.base_data_provider import AbstractDataProvider
from market_data.tushare_data_provider import TuShareDataProvider
from market_data.akshare_data_provider import AkShareDataProvider
from market_data import data_definition
from market_data.models import FutureHoldingData, StockIndexWeightData

CHINA_TZ = timezone("Asia/Shanghai")
UTC_TZ = timezone("UTC")

logger = logging.getLogger(__name__)

class SmartDataProvider(AbstractDataProvider):
    def __init__(self, database_manager=None):        
        super().__init__(database_manager)
        
        self.akshare_provider = AkShareDataProvider(database_manager)
        self.tushare_provider = TuShareDataProvider(database_manager)
        
    def download_data(self, data_requirement):
        if type(data_requirement) == data_definition.FutureHoldingData:
            return self.akshare_provider.download_data(data_requirement)
        if type(data_requirement) == data_definition.FutureTickData:
            return self.tushare_provider.download_data(data_requirement)
        if type(data_requirement) == data_definition.IndexData:
            return self.tushare_provider.download_data(data_requirement)
        if type(data_requirement) == data_definition.IndexWeightData:
            return self.tushare_provider.download_data(data_requirement)
        if type(data_requirement) == data_definition.ConvertibleBondDailyData:
            return self.tushare_provider.download_data(data_requirement)
        if type(data_requirement) == data_definition.StockBasicInfoData:
            return self.tushare_provider.download_stock_basic_info_data(data_requirement)
        if type(data_requirement) == data_definition.StockHoldingData:
            return self.tushare_provider.download_stock_holding_data(data_requirement)
        if type(data_requirement) == data_definition.StockDailyData:
            try:
                return self.tushare_provider.download_data(data_requirement)
            except:
                logger.warning("Fall back to akshare for stock data")
                return self.akshare_provider.download_data(data_requirement)
        if type(data_requirement) == data_definition.FundNavData:
            return self.tushare_provider.download_fund_nav_data(data_requirement)
        logger.error(f"Unknown data: {data_requirement}")
        
    def get_fx_quote_for_cny(self, currency):
        return self.akshare_provider.get_fx_quote_for_cny(currency)
        
    def get_future_info_for_symbol(self, symbol):
        return self.akshare_provider.get_future_info_for_symbol(symbol)
    
    def update_future_info(self):
        return self.akshare_provider.update_future_info()
    
    def get_stock_list_for_index(self, data_requirement):
        stock_list = (StockIndexWeightData
                      .select(StockIndexWeightData.stock_symbol, 
                              StockIndexWeightData.stock_exchange, 
                              peewee.fn.COUNT(StockIndexWeightData.id))
                      .where(StockIndexWeightData.index_symbol==data_requirement.symbol)
                      .group_by(StockIndexWeightData.stock_symbol).dicts())
        return stock_list
    
    def download_all_index_stock_basic_info_data(self, data_requirement):
        stock_list = self.get_stock_list_for_index(data_requirement)
        for stock_dict in stock_list:
            temp_data_requirement = data_definition.StockBasicInfoData(symbol=stock_dict["stock_symbol"], 
                                                   start_date=datetime(2006,1,1), 
                                                   exchange=Exchange(stock_dict["stock_exchange"]))
            try:
                self.download_data(temp_data_requirement)
            except Exception as e:
                logger.error(f"Failed to download stock basic info data for {stock_dict} {e}")
    
    def download_all_index_stock_holding_data(self, data_requirement):
        stock_list = self.get_stock_list_for_index(data_requirement)
        for stock_dict in stock_list:
            temp_data_requirement = data_definition.StockHoldingData(symbol=stock_dict["stock_symbol"], 
                                                   start_date=datetime(2006,1,1), 
                                                   exchange=Exchange(stock_dict["stock_exchange"]))
            try:
                self.download_data(temp_data_requirement)
            except Exception as e:
                logger.error(f"Failed to download stock holding data for {stock_dict} {e}")
    
    
    def download_all_index_stock_price_data(self, data_requirement):
        stock_list = self.get_stock_list_for_index(data_requirement)
        for stock_dict in stock_list:
            temp_data_requirement = data_definition.StockDailyData(symbol=stock_dict["stock_symbol"], 
                                                   start_date=datetime(2006,1,1), 
                                                   exchange=Exchange(stock_dict["stock_exchange"]))
            try:
                self.download_data(temp_data_requirement)
            except Exception as e:
                logger.error(f"Failed to download stock data for {stock_dict}")