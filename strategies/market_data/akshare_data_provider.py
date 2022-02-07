from vnpy.trader.object import BarData
from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.database import get_database

import akshare as ak
from pytz import timezone
import peewee

from datetime import datetime, timedelta, date
import time
from collections import defaultdict

from market_data import data_definition
from market_data.models import FutureInfo, FutureHoldingData
from market_data.base_data_provider import AbstractDataProvider

import tushare as ts

CHINA_TZ = timezone("Asia/Shanghai")
UTC_TZ = timezone("UTC")
        
class AkShareDataProvider(AbstractDataProvider): 
    def get_fx_quote_for_cny(self, currency):
        if currency == "CNY":
            return 1
        
        if hasattr(self, "fx_quote_cache"):
            fx_df = self.fx_quote_cache
        else:
            fx_df = ak.fx_spot_quote()
            self.fx_quote_cache = fx_df
        target_line = fx_df[fx_df["ccyPair"] == f"{currency}/CNY"]
        if len(target_line) == 0:
            return None
        return float(target_line.iloc[0].bidPrc)
    
    def get_last_finish_trading_day(self):
        if self.trade_calendar_list is None:
            self.trade_calendar_list = list(ak.tool_trade_date_hist_sina()["trade_date"])
            
        curr_date = date.today()

        is_trading_date = False
        while not is_trading_date:
            if curr_date in self.trade_calendar_list:
                is_trading_date = True
                break
            curr_date -= timedelta(days=1)
            
        return curr_date
    
    def get_next_trading_day(self, curr_date):
        if self.trade_calendar_list is None:
            self.trade_calendar_list = list(ak.tool_trade_date_hist_sina()["trade_date"])
            
        curr_date += timedelta(days=1)
        while True:
            if curr_date in self.trade_calendar_list:
                return curr_date
            curr_date += timedelta(days=1)
    
    def convert_ak_df_to_bar_data(self, input_df, symbol, exchange, interval, price_column=None, date_format="%Y%m%d"):
        result_bars = []
        for index, row in input_df.iterrows():
            default_price = 0
            if price_column:
                default_price = row[price_column]
               
            
            if type(row['date']) == str:
                trade_date = UTC_TZ.localize(datetime.strptime(row['date'], date_format))
            elif type(row['date']) == date:
                trade_date = UTC_TZ.localize(datetime(row['date'].year, row['date'].month, row['date'].day))
            
            new_bar = BarData(gateway_name='akshare', 
                              symbol=symbol, 
                              exchange=exchange, 
                              datetime=trade_date,
                              interval=interval,
                              volume=row.get("volume", row.get("vol", 0)),
                              open_price=row.get("open", default_price),
                              high_price=row.get("high", default_price),
                              low_price=row.get("low", default_price),
                              close_price=row.get("close", default_price)
                             )
            result_bars.append(new_bar)
        return result_bars
    
    def download_index_data(self, data_requirement):
        latest_day = self.get_latest_date_for_symbol(data_requirement.symbol, data_requirement)
        today = self.get_last_finish_trading_day()
        if latest_day and (latest_day.strftime("%Y%m%d") == today.strftime("%Y%m%d")):
            return
        
        exchange_prefix_mapping = {
            Exchange.SSE: "sh",
            Exchange.SZSE: "sz",
        }
        
        sina_symbol = exchange_prefix_mapping[data_requirement.exchange] + data_requirement.symbol
        
        stock_zh_index_daily_df = ak.stock_zh_index_daily(symbol=sina_symbol)
        
        result_bars = self.convert_ak_df_to_bar_data(stock_zh_index_daily_df,
                                       data_requirement.symbol,
                                       data_requirement.exchange,
                                       data_requirement.interval,
                                       date_format="%Y-%m-%d")
        self.database_manager.save_bar_data(result_bars)
        
    
    def download_future_holding_data(self, data_requirement, start_date=None):
        self.database_manager.db.create_tables([FutureHoldingData])
        
        if start_date is None:
            latest_day = list(FutureHoldingData.select(peewee.fn.MAX(FutureHoldingData.trade_date))
                              .where(FutureHoldingData.exchange==data_requirement.exchange.value).dicts())[0]["trade_date"]
            if latest_day is None:
                latest_day = date(1990,1,1)
            latest_day = self.get_next_trading_day(latest_day)
        else:
            latest_day = start_date            
        
        today = self.get_last_finish_trading_day()
        
        while latest_day < today:
            if data_requirement.exchange.value == "CFFEX":
                rank_table_dict = ak.get_cffex_rank_table(date=latest_day.strftime("%Y%m%d"))
            elif data_requirement.exchange.value == "SHFE":
                rank_table_dict = ak.get_shfe_rank_table(date=latest_day.strftime("%Y%m%d"))
            elif data_requirement.exchange.value == "CZCE":
                rank_table_dict = ak.get_czce_rank_table(date=latest_day.strftime("%Y%m%d"))
                
            for symbol, df in rank_table_dict.items():
                symbol = symbol.upper()
                new_object_map = {}
                for index, row in df.iterrows():
                    # long
                    if row["long_party_name"] not in new_object_map:
                        new_holding_data = FutureHoldingData(
                            trade_date=latest_day,
                            symbol=symbol,
                            exchange=data_requirement.exchange.value,
                            broker=row["long_party_name"])
                        new_object_map[row["long_party_name"]] = new_holding_data
                    new_object_map[row["long_party_name"]].long_hld = row["long_open_interest"]
                    new_object_map[row["long_party_name"]].long_chg = row["long_open_interest_chg"]

                    # short
                    if row["short_party_name"] not in new_object_map:
                        new_holding_data = FutureHoldingData(
                            trade_date=latest_day,
                            symbol=symbol,
                            exchange=data_requirement.exchange.value,
                            broker=row["short_party_name"])
                        new_object_map[row["short_party_name"]] = new_holding_data
                    new_object_map[row["short_party_name"]].short_hld = row["short_open_interest"]
                    new_object_map[row["short_party_name"]].short_chg = row["short_open_interest_chg"]

                    # vol
                    if row["vol_party_name"] not in new_object_map:
                        new_holding_data = FutureHoldingData(
                            trade_date=latest_day,
                            symbol=symbol,
                            exchange=data_requirement.exchange.value,
                            broker=row["vol_party_name"])
                        new_object_map[row["vol_party_name"]] = new_holding_data
                    new_object_map[row["vol_party_name"]].vol = row["vol"]
                    new_object_map[row["vol_party_name"]].vol_chg = row["vol_chg"]
                # None 表示总数，不需要储存进来
                if None in new_object_map:
                    del new_object_map[None]
                FutureHoldingData.bulk_create(list(new_object_map.values()))
                print(f"Added {len(new_object_map)} FutureHoldingData for {latest_day} {data_requirement.exchange.value}")
            latest_day = self.get_next_trading_day(latest_day)
    
    def download_all_future_tick_data_for_market(self, data_requirement):
        exchange = data_requirement.exchange
        latest_day = UTC_TZ.localize(data_requirement.start_date).date()
        
        today = self.get_last_finish_trading_day()
        no_progress_count = 0
        while latest_day < today:
            latest_day_symbol = data_requirement.symbol + "99"
            new_latest_day = self.get_latest_date_for_symbol(latest_day_symbol, data_requirement)
            if new_latest_day:
                if new_latest_day > latest_day:
                    latest_day = new_latest_day
            
            if today > (latest_day + timedelta(days=self.download_step_days)):
                daily_exchange_price_df = ak.get_futures_daily(start_date=latest_day.strftime("%Y%m%d"), 
                                                               end_date=(latest_day + timedelta(days=self.download_step_days)).strftime("%Y%m%d"), 
                                                               market=data_requirement.exchange.value, 
                                                               index_bar=True)
            else:
                daily_exchange_price_df = ak.get_futures_daily(start_date=latest_day.strftime("%Y%m%d"), 
                                                               end_date=today.strftime("%Y%m%d"), 
                                                               market=data_requirement.exchange.value, 
                                                               index_bar=True)
            daily_exchange_price_df["open"] = daily_exchange_price_df["open"].fillna(daily_exchange_price_df["close"])
            daily_exchange_price_df["high"] = daily_exchange_price_df["high"].fillna(daily_exchange_price_df["close"])
            daily_exchange_price_df["low"] = daily_exchange_price_df["low"].fillna(daily_exchange_price_df["close"])
            
            symbol_map = defaultdict(list)
            
            for index, row in daily_exchange_price_df.iterrows():
                trade_date = UTC_TZ.localize(datetime.strptime(row['date'], '%Y%m%d'))
                
                new_bar = BarData(gateway_name='akshare', 
                                  symbol=row["symbol"], 
                                  exchange=data_requirement.exchange, 
                                  datetime=trade_date,
                                  interval=Interval.DAILY,
                                  volume=row["volume"],
                                  open_price=row["open"],
                                  high_price=row["high"],
                                  low_price=row["low"],
                                  close_price=row["close"]
                                 )
                symbol_map[row["symbol"]].append(new_bar)
                
            for symbol, bar_list in symbol_map.items():
                print(f"Saving {symbol}")
                self.database_manager.save_bar_data(bar_list)                                                      
    
    def download_stock_data(self, data_requirement, force=False):        
        latest_day = self.get_latest_date_for_symbol(data_requirement.symbol, data_requirement)
        if latest_day is None:
            latest_day = date(1990,1,1)
        today = self.get_last_finish_trading_day()

        if not force:
            if latest_day and (latest_day.strftime("%Y%m%d") == today.strftime("%Y%m%d")):
                print(f"No new data needed for {data_requirement.symbol}")
                return
        
        result_bars = []
        if data_requirement.exchange in [Exchange.NYSE, Exchange.NASDAQ]:
            all_stock_symbol = list(ak.stock_us_spot_em()["代码"])
            find_symbol_list = [x for x in all_stock_symbol if x.endswith(f".{data_requirement.symbol}")]
            if len(find_symbol_list) == 0:
                # ADR code 153
                ak_symbol = f"153.{data_requirement.symbol}"
            else:
                ak_symbol = find_symbol_list[0]
            stock_us_hist_df = ak.stock_us_hist(symbol=ak_symbol, start_date=latest_day.strftime("%Y%m%d"), end_date=today.strftime("%Y%m%d"))
            
            for index, row in stock_us_hist_df.iterrows():
                trade_date = UTC_TZ.localize(datetime.strptime(row['日期'], '%Y-%m-%d'))
                
                new_bar = BarData(gateway_name='akshare', 
                                  symbol=data_requirement.symbol, 
                                  exchange=data_requirement.exchange, 
                                  datetime=trade_date,
                                  interval=Interval.DAILY,
                                  volume=row["成交量"],
                                  open_price=row["开盘"],
                                  high_price=row["最高"],
                                  low_price=row["最低"],
                                  close_price=row["收盘"]
                                 )
                result_bars.append(new_bar)

        print(f"Downloaded {len(result_bars)} bars for {data_requirement.symbol}") 
        self.database_manager.save_bar_data(result_bars)
    
    def download_data(self, data_requirement):
        if type(data_requirement) == data_definition.FutureHoldingData:
            return self.download_future_holding_data(data_requirement)
        if type(data_requirement) == data_definition.FutureTickData:
            return self.download_all_future_tick_data_for_market(data_requirement)
        if type(data_requirement) == data_definition.IndexData:
            return self.download_index_data(data_requirement)
        if type(data_requirement) == data_definition.StockDailyData:
            if data_requirement.exchange.value in ["HKSE", "NASDAQ", "NYSE"]:
                return self.download_stock_data(data_requirement, force=True)
            else:
                return self.download_stock_data(data_requirement)
        
    def update_future_info(self):
        self.database_manager.db.create_tables([FutureInfo])
        
        futures_rule_df = ak.futures_rule(trade_date="20211206")
        if len(futures_rule_df) > 0:
            FutureInfo.delete().execute()
            for index, row in futures_rule_df.iterrows():
                if row["交易保证金比例"][-1] != "%":
                    continue
                margin_rate = float(row["交易保证金比例"][:-1]) / 100
                FutureInfo.create(future_symbol=row["代码"],
                                  margin_rate=margin_rate,
                                  multiplier=float(row["合约乘数"]),
                                  priceticks=float(row["最小变动价位"])
                                 )
                
    def get_future_info_for_symbol(self, symbol):
        return FutureInfo.get_or_none(FutureInfo.future_symbol==symbol)
