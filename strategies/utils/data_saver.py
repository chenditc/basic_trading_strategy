from vnpy.trader.object import BarData
from vnpy.trader.database import database_manager
from vnpy.trader.constant import Interval

from datetime import datetime

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