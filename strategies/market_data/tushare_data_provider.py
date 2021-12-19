from datetime import datetime, timedelta, date

from vnpy.trader.object import BarData
from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.database import get_database
import tushare as ts
from pytz import timezone
import pandas as pd
import numpy as np
import peewee

from utils.system_configs import tushare_config
from market_data.base_data_provider import AbstractDataProvider
from market_data import data_definition
from market_data.models import FutureHoldingData

CHINA_TZ = timezone("Asia/Shanghai")
UTC_TZ = timezone("UTC")

class TuShareDataProvider(AbstractDataProvider):
    def __init__(self, database_manager=None):        
        super().__init__(database_manager)
        
        self.trade_calendar_map = {}
        self.pro = ts.pro_api(tushare_config["token"])

    def load_trade_calendar_map(self, exchange):
        if exchange not in self.trade_calendar_map:
            df = self.pro.trade_cal(exchange=exchange, start_date='19000101', end_date='20501231')
            self.trade_calendar_map[exchange] = list(df[df["is_open"] == 1]["cal_date"])
        
    def get_next_trading_day(self, curr_date, exchange="CFFEX"):
        self.load_trade_calendar_map(exchange)
        curr_date += timedelta(days=1)
        while True:
            if curr_date.strftime("%Y%m%d") in self.trade_calendar_map[exchange]:
                return curr_date
            curr_date += timedelta(days=1)
        
    def get_last_finish_trading_day(self, exchange="CFFEX"):
        self.load_trade_calendar_map(exchange)
        
        curr_date = date.today()
        if datetime.now(CHINA_TZ).hour < 17:
            # Still in trading hour, skip today
            curr_date -= timedelta(days=1)

        is_trading_date = False
        while not is_trading_date:
            if curr_date.strftime("%Y%m%d") in self.trade_calendar_map[exchange]:
                is_trading_date = True
                break
            curr_date -= timedelta(days=1)
            
        return curr_date
    
    def convert_ts_df_to_bar_data(self, input_df, symbol, exchange, interval=Interval.DAILY, price_column=None, date_format="%Y%m%d"):
        input_df["open"] = input_df["open"].fillna(input_df["close"])
        input_df["low"] = input_df["low"].fillna(input_df["close"])
        input_df["high"] = input_df["high"].fillna(input_df["close"])
        input_df = input_df.replace({np.nan: 0})
        result_bars = []
        for index, row in input_df.iterrows():
            if symbol is None:
                symbol, suffix = row['ts_code'].split(".")

            trade_date = UTC_TZ.localize(datetime.strptime(row['trade_date'], date_format))
            new_bar = BarData(gateway_name='tushare', 
                              symbol=symbol, 
                              exchange=exchange, 
                              datetime=trade_date,
                              interval=interval,
                              volume=row['vol'],
                              open_price=row['open'],
                              high_price=row['high'],
                              low_price=row['low'],
                              close_price=row['close'],
                              open_interest=row.get("oi", 0)
                             )

            result_bars.append(new_bar)
        return result_bars
    
    def download_index_data(self, data_requirement):
        latest_day = self.get_latest_date_for_symbol(data_requirement.symbol, data_requirement)
        if latest_day is None:
            latest_day = date(1990,1,1)
        today = self.get_last_finish_trading_day()
        if latest_day and (latest_day.strftime("%Y%m%d") == today.strftime("%Y%m%d")):
            print(f"No new data needed for {data_requirement.symbol}")
            return
        
        exchange_suffix_mapping = {
            Exchange.SSE: ".SH",
            Exchange.SZSE: ".SZ",
        }
        ts_code = data_requirement.symbol + exchange_suffix_mapping[data_requirement.exchange]

        
        index_df = self.pro.index_daily(ts_code=ts_code, start_date=latest_day.strftime("%Y%m%d"), end_date=today.strftime("%Y%m%d"))
        result_bars = self.convert_ts_df_to_bar_data(index_df, 
                                                     data_requirement.symbol, 
                                                     data_requirement.exchange)
        print(f"Downloaded {len(result_bars)} bars for {ts_code}") 
        self.database_manager.save_bar_data(result_bars)
        
    def download_stock_data(self, data_requirement):
        latest_day = self.get_latest_date_for_symbol(data_requirement.symbol, data_requirement)
        if latest_day is None:
            latest_day = date(1990,1,1)
        today = self.get_last_finish_trading_day()
        if latest_day and (latest_day.strftime("%Y%m%d") == today.strftime("%Y%m%d")):
            print(f"No new data needed for {data_requirement.symbol}")
            return
        
        exchange_suffix_mapping = {
            Exchange.SSE: ".SH",
            Exchange.SZSE: ".SZ",
        }
        ts_code = data_requirement.symbol + exchange_suffix_mapping[data_requirement.exchange]

        
        index_df = self.pro.daily(ts_code=ts_code, start_date=latest_day.strftime("%Y%m%d"), end_date=today.strftime("%Y%m%d"))
        result_bars = self.convert_ts_df_to_bar_data(index_df, 
                                                     data_requirement.symbol, 
                                                     data_requirement.exchange)
        print(f"Downloaded {len(result_bars)} bars for {ts_code}") 
        self.database_manager.save_bar_data(result_bars)

    def download_future_holding_data(self, data_requirement):
        latest_day = list(FutureHoldingData.select(peewee.fn.MAX(FutureHoldingData.trade_date))
                          .where(FutureHoldingData.exchange==data_requirement.exchange.value).dicts())[0]["trade_date"]
        if latest_day is None:
            latest_day = date(1990,1,1)
        else:
            latest_day = self.get_next_trading_day(latest_day)
        
        today = self.get_last_finish_trading_day()
        
        while latest_day < today:
            df = self.pro.fut_holding(trade_date=latest_day.strftime("%Y%m%d"), 
                                      exchange=data_requirement.exchange.value)
            df = df.replace({np.nan: None})
            new_object_list = []
            for index, row in df.iterrows():
                new_object_list.append(FutureHoldingData(
                    trade_date = latest_day,
                    symbol = row["symbol"],
                    exchange = data_requirement.exchange.value,
                    broker = row["broker"],
                    vol = row.get("vol"),
                    vol_chg = row.get("vol_chg"),
                    long_hld = row.get("long_hld"),
                    long_chg = row.get("long_chg"),
                    short_hld = row.get("short_hld"),
                    short_chg = row.get("short_chg")
                ))
            FutureHoldingData.bulk_create(new_object_list)
            print(f"Added {len(new_object_list)} FutureHoldingData for {latest_day} {data_requirement.exchange.value}")
            latest_day = self.get_next_trading_day(latest_day)
            
    def download_all_future_tick_data(self, data_requirement):
        df = self.pro.fut_basic(exchange=data_requirement.exchange.value, 
                                fut_type='1', 
                                fields='ts_code,symbol,list_date,delist_date')
        all_monthly_future_df = df[df["symbol"].str.contains(data_requirement.symbol)]
        
        for index, row in all_monthly_future_df.iterrows():
            latest_day = self.get_latest_date_for_symbol(row["symbol"], data_requirement)
            if latest_day and latest_day.strftime("%Y%m%d") >= row["delist_date"]:
                print(f"Skipping finished future {row}")
                continue
            if date.today().strftime("%Y%m%d") <= row["list_date"]:
                print(f"Skipping not started future {row}")
                continue
            print(f"downloading {row}")
            daily_price_df = self.pro.fut_daily(ts_code=row["ts_code"], 
                                                start_date=row["list_date"], 
                                                end_date=row["delist_date"])
            result_bars = self.convert_ts_df_to_bar_data(daily_price_df, 
                                                         row["symbol"], 
                                                         data_requirement.exchange)
            self.database_manager.save_bar_data(result_bars)
            print(f"Saving {row}")

        
    def download_data(self, data_requirement):
        if type(data_requirement) == data_definition.FutureHoldingData:
            return self.download_future_holding_data(data_requirement)
        if type(data_requirement) == data_definition.FutureTickData:
            return self.download_all_future_tick_data(data_requirement)
        if type(data_requirement) == data_definition.IndexData:
            return self.download_index_data(data_requirement)
        if type(data_requirement) == data_definition.StockDailyData:
            return self.download_stock_data(data_requirement)
