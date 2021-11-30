from vnpy.trader.object import BarData
from vnpy.trader.database import database_manager
from vnpy.trader.constant import Exchange, Interval
from datetime import datetime
import time

import akshare as ak

from pytz import timezone
CHINA_TZ = timezone("Asia/Shanghai")
UTC_TZ = timezone("UTC")

def save_tushare_df(df, exchange):
    tushare_bars = []
    for index, row in df.iterrows():
        symbol, suffix = row['ts_code'].split(".")

        trade_date = UTC_TZ.localize(datetime.strptime(row['trade_date'], '%Y%m%d'))
        new_bar = BarData(gateway_name='tushare', 
                          symbol=symbol, 
                          exchange=exchange, 
                          datetime=trade_date,
                          interval=Interval.DAILY,
                          volume=row['vol'],
                          open_price=row['open'],
                          high_price=row['high'],
                          low_price=row['low'],
                          close_price=row['close']
                         )

        tushare_bars.append(new_bar)
        
    tushare_bars.reverse()
    database_manager.delete_bar_data(symbol=symbol, exchange=exchange, interval=Interval.DAILY)
    database_manager.save_bar_data(tushare_bars)

def get_latest_date_for_symbol(symbol, exchange, interval=Interval.DAILY):
    bar_list = database_manager.load_bar_data(symbol, 
                                              exchange=exchange, 
                                              interval=interval, 
                                              start=datetime.strptime("19000101", '%Y%m%d'), 
                                              end=datetime.strptime("20550101", '%Y%m%d'))
    if len(bar_list) == 0:
        return
    return bar_list[-1].datetime

def save_future_holding_data(df, exchange):
    CHINA_TZ = timezone("Asia/Shanghai")
    UTC_TZ = timezone("UTC")

    tushare_bars = []
    for index, row in df.iterrows():
        for column_name in ["long_open_interest_chg_top20", "short_open_interest_chg_top20"]:
            symbol = row['symbol'] + "_" + column_name
            price = row[column_name]

            trade_date = UTC_TZ.localize(datetime.strptime(row['date'], '%Y%m%d'))
            print(symbol, price, trade_date)

            new_bar = BarData(gateway_name='tushare', 
                              symbol=symbol, 
                              exchange=exchange, 
                              datetime=trade_date,
                              interval=Interval.DAILY,
                              volume=0,
                              open_price=price,
                              high_price=price,
                              low_price=price,
                              close_price=price
                             )
            tushare_bars.append(new_bar)
    print(f"Saving new bars: {len(tushare_bars)}")
    database_manager.save_bar_data(tushare_bars)

def download_future_holding_data_set(start_day, end_day, symbols, restart=False):
    exchange=Exchange.CFFEX
    if restart:
        for symbol in symbols:
            symbol_to_delete = symbol + "_long_open_interest_chg_top20"
            database_manager.delete_bar_data(symbol=symbol_to_delete, exchange=exchange, interval=Interval.DAILY)
    
    latest_day = start_day
    
    no_progress_count = 0
    while latest_day < end_day:
        latest_symbol = symbols[0] + "_long_open_interest_chg_top20"
        print("Latest symbol:", latest_symbol)
        latest_datetime = get_latest_date_for_symbol(symbol=latest_symbol, exchange=exchange)
        print("Latest date:", latest_datetime)
        if latest_datetime:
            new_latest_day = latest_datetime.strftime('%Y%m%d')
            if new_latest_day > latest_day:
                latest_day = new_latest_day
            else:
                no_progress_count += 1
                time.sleep(5)
                
        get_rank_sum_daily_df = ak.get_rank_sum_daily(start_day=latest_day, end_day=end_day, vars_list=symbols)
        if len(get_rank_sum_daily_df) > 0:
            save_future_holding_data(get_rank_sum_daily_df, exchange)
        
        if no_progress_count > 5:
            print("No more data, stop")
            break