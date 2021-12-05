from datetime import date, datetime
import re

from .models import FutureInfo

from vnpy.trader.database import get_database
from vnpy.trader.constant import Interval, Exchange

from market_data.akshare_data_provider import AkShareDataProvider
from asset_management.models import FutureInfo, CurrentPosition, PositionHistory

def get_future_margin_multiplier_for_symbol(symbol):
    future_symbol = re.split(r'\d', symbol)[0]
    future_info = FutureInfo.get_or_none(FutureInfo.future_symbol==future_symbol)
    if future_info:
        return float(future_info.margin_rate), float(future_info.multiplier)
    else:
        return 1, 1

def calculate_latest_position_history():
    today = date.today()
    database_manager = get_database()
    data_provider = AkShareDataProvider(database_manager)
    data_provider.update_future_info()
    
    # Get all current position with price
    all_current_position = CurrentPosition.select()
    
    # calculate position history
    for curr_position in all_current_position:
        no_suffix_symbol = curr_position.symbol.split(".")[0]
        
        related_symbol_bar_list = database_manager.load_bar_data(symbol=no_suffix_symbol, 
                                 exchange=Exchange(curr_position.exchange),
                                 interval=Interval.DAILY,
                                 start=date(2000,1,1),
                                 end=datetime.now())
        last_price_day = related_symbol_bar_list[-1].datetime.date()
        if last_price_day != today:
            print(f"No price for {curr_position.symbol} at day {today}, lastest day is {last_price_day}")
            #continue
        
        price = related_symbol_bar_list[-1].close_price
        
        margin_rate, multiplier = get_future_margin_multiplier_for_symbol(curr_position.symbol)
        net_value = price * float(curr_position.volume) * multiplier
        margin_value = net_value * margin_rate
        
        PositionHistory.insert(symbol=curr_position.symbol,
                               exchange=curr_position.exchange,
                               volume=curr_position.volume,
                               platform=curr_position.platform,
                               pos_date=today,
                               net_value=net_value,
                               margin_value=margin_value).on_conflict_replace().execute()
                               