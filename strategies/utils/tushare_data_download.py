from datetime import datetime, timedelta
import time

from vnpy.trader.constant import Exchange

from utils import symbol_generator
from utils import data_saver

from .system_configs import tushare_config

import tushare
tushare.set_token(tushare_config["token"])

def download_daily_price(ts_code, asset, exchange, start_date="19000101", end_date="20500101"):
    # 资产类别：E股票 I沪深指数 C数字货币 FT期货 FD基金 O期权 CB可转债（v1.2.39），默认E
    print(f"Downloading asset {asset} daily price for {ts_code} from tushare")
    
    try:
        df = tushare.pro_bar(ts_code=ts_code, asset=asset, start_date=start_date, end_date=end_date)
        if len(df) == 0:
            return False
        df["open"] = df["open"].fillna(df["close"])
        df["low"] = df["low"].fillna(df["close"])
        df["high"] = df["high"].fillna(df["close"])
    except IOError as e:
        print(f"Failed to download for {ts_code}")
        print(e)
        return False
    data_saver.save_tushare_df(df, exchange)
    print(f"Updated {len(df)} records for {ts_code}")
    return True

def download_future_data_until_success(start_date, end_date, prefix, max_retry = 10, retry_interval = 60, step_days=32):
    some_success = False
    retry_count = 0
    while some_success is False:
        symbol_list = symbol_generator.get_index_future_symbol(start_date, 
                                             end_date, 
                                             prefix=prefix,
                                             step_days=step_days)
        for symbol in symbol_list:
            some_success |= download_daily_price(symbol + ".CFX", asset='FT', exchange=Exchange.CFFEX)
        
        if retry_count < max_retry and (not some_success):
            retry_count += 1
            time.sleep(retry_interval)
            print(f"Failed to download future data, sleep {retry_interval} seconds and retry...")
            
    if not some_success:
        raise Exception("Failed to prepare future data")
        
def prepare_ic_data_set(recent_only=True):
    some_success = False
    download_daily_price('000905.SH', asset='I', exchange=Exchange.SSE)

    start_date = datetime(2016,1,1)
    if recent_only:
        start_date = datetime.today() - timedelta(days=60)
    
    download_future_data_until_success(start_date=start_date, end_date=datetime.today(), prefix="IC")
    
    local_symbol_list = ['000905.SSE']
    for symbol in symbol_generator.get_index_future_symbol(datetime(2016,1,1), datetime.today(), prefix="IC"):
        local_symbol_list.append(symbol + ".CFFEX")

    return local_symbol_list
        
def prepare_if_data_set(recent_only=True):
    download_daily_price('000300.SH', asset='I', exchange=Exchange.SSE)
    
    start_date=datetime(2016,1,1)
    if recent_only:
        start_date = datetime.today() - timedelta(days=60)
    
    download_future_data_until_success(start_date=start_date, end_date=datetime.today(), prefix="IF")
        
    local_symbol_list = ['000300.SSE']
    for symbol in symbol_generator.get_index_future_symbol(datetime(2016,1,1), datetime.today(), prefix="IF"):
        local_symbol_list.append(symbol + ".CFFEX")

    return local_symbol_list
        
def prepare_bond_future_data_set(recent_only=True):
    start_date=datetime(2015,12,1)
    
    download_future_data_until_success(start_date=start_date, end_date=datetime.today(), prefix="TF", step_days=92)
    for symbol in symbol_generator.get_index_future_symbol(datetime(2015,12,1), datetime.today(), prefix="TF", step_days=92):
        local_symbol_list.append(symbol + ".CFFEX")

    return local_symbol_list
    
if __name__ == "__main__":
    prepare_ic_data_set()