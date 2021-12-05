from vnpy.trader.object import BarData
from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.database import get_database

import akshare as ak
from pytz import timezone

from datetime import datetime, timedelta, date
import time
from collections import defaultdict

from market_data import data_definition
from asset_management.models import FutureInfo


CHINA_TZ = timezone("Asia/Shanghai")
UTC_TZ = timezone("UTC")

class AbstractDataProvider():
    def __init__(self, database_manager):
        self.database_manager = database_manager
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
    
    def get_last_finish_trading_day(self):
        if self.trade_calendar_list is None:
            self.trade_calendar_list = list(ak.tool_trade_date_hist_sina()["trade_date"])
            
        curr_date = date.today()
        if datetime.now(CHINA_TZ).hour < 17:
            # Still in trading hour, skip today
            curr_date -= timedelta(days=1)

        is_trading_date = False
        while not is_trading_date:
            if curr_date in self.trade_calendar_list:
                is_trading_date = True
                break
            curr_date -= timedelta(days=1)
            
        return curr_date
        
class AkShareDataProvider(AbstractDataProvider):     
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
        
    
    def download_future_holding_data(self, data_requirement):
        exchange = data_requirement.exchange
        latest_day = UTC_TZ.localize(data_requirement.start_date).date()
        
        today = self.get_last_finish_trading_day()
        
        no_progress_count = 0
        while latest_day < today:
            latest_day_symbol = data_requirement.long_open_chg_top20_field
            new_latest_day = self.get_latest_date_for_symbol(latest_day_symbol, data_requirement)
            if new_latest_day:
                if new_latest_day > latest_day:
                    latest_day = new_latest_day

            get_rank_sum_daily_df = ak.get_rank_sum_daily(start_day=latest_day.strftime("%Y%m%d"), 
                                                          end_day=today.strftime("%Y%m%d"), 
                                                          vars_list=[data_requirement.symbol])
            if len(get_rank_sum_daily_df) > 0:
                summary_symbol_df = get_rank_sum_daily_df[get_rank_sum_daily_df["symbol"]==data_requirement.symbol]
                result_bars = self.convert_ak_df_to_bar_data(summary_symbol_df, 
                                                             data_requirement.long_open_chg_top20_field, 
                                                             data_requirement.exchange, 
                                                             data_requirement.interval,
                                                            price_column="long_open_interest_chg_top20")
                self.database_manager.save_bar_data(result_bars)
                
                result_bars = self.convert_ak_df_to_bar_data(summary_symbol_df, 
                                                             data_requirement.short_open_chg_top20_field, 
                                                             data_requirement.exchange, 
                                                             data_requirement.interval,
                                                            price_column="short_open_interest_chg_top20")
                self.database_manager.save_bar_data(result_bars)
    
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
    
    def download_data(self, data_requirement):
        if type(data_requirement) == data_definition.FutureHoldingData:
            return self.download_future_holding_data(data_requirement)
        if type(data_requirement) == data_definition.FutureTickData:
            return self.download_all_future_tick_data_for_market(data_requirement)
        if type(data_requirement) == data_definition.IndexData:
            return self.download_index_data(data_requirement)

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
                                  multiplier=float(row["合约乘数"]))