from datetime import date, datetime
import re
import logging

from vnpy.trader.database import get_database
from vnpy.trader.constant import Interval, Exchange

from asset_management.models import CurrentPosition, PositionHistory
from market_data.models import FutureInfo
from market_data.smart_data_provider import SmartDataProvider
from market_data.data_definition import get_daily_price_data_definition, FxDailyData

logger = logging.getLogger(__name__)

def get_future_margin_multiplier_for_symbol(symbol):
    future_symbol = re.split(r'\d', symbol)[0]
    future_info = FutureInfo.get_or_none(FutureInfo.future_symbol==future_symbol)
    if future_info:
        return float(future_info.margin_rate), float(future_info.multiplier)
    else:
        return 1, 1    
    
def get_latest_price(no_suffix_symbol, exchange, data_provider, database_manager):
    today = date.today()
    # Download price data
    data_definition = get_daily_price_data_definition(no_suffix_symbol, exchange)
    if type(data_definition) == FxDailyData:
        return 1, today
    
    if data_definition is None:
        logger.error(f"Unknown price data: {curr_position.symbol}")
        return None, today

    try:
        data_provider.download_data(data_definition)
    except Exception as e:
        logger.error(f"Failed to download data: {e}")
        return None, today
            
    # Get latest price data
    related_symbol_bar_list = database_manager.load_bar_data(symbol=no_suffix_symbol, 
                             exchange=exchange,
                             interval=Interval.DAILY,
                             start=data_definition.start_date,
                             end=datetime.now())
    if len(related_symbol_bar_list) == 0:
        logger.error(f"No price data for {curr_position.symbol}")
        return None, today
    last_price_day = related_symbol_bar_list[-1].datetime.date()
    
    if last_price_day != today:
        logger.info(f"No price for {no_suffix_symbol} at day {today}, lastest day is {last_price_day}")
    price = related_symbol_bar_list[-1].close_price
    return price, last_price_day
    
def calculate_latest_position_history():    
    today = date.today()
    database_manager = get_database()
    data_provider = SmartDataProvider()
    data_provider.update_future_info()
    
    # Get all current position with price
    all_current_position = CurrentPosition.select()
    
    # calculate position history
    new_position_history_list = []
    for curr_position in all_current_position:
        no_suffix_symbol = curr_position.symbol.split(".")[0]
        try:
            exchange = Exchange(curr_position.exchange)
        except ValueError:
            logger.error(f"Unknown exchange: {curr_position.exchange}")
            continue

        price, last_price_day = get_latest_price(no_suffix_symbol, exchange, data_provider, database_manager)
        if price is None:
            continue
        
        # Get calcualte margin value and net value
        margin_rate, multiplier = get_future_margin_multiplier_for_symbol(curr_position.symbol)
        net_value = price * float(curr_position.volume) * multiplier
        margin_value = net_value * margin_rate
        
        # Get currency rate and convert net value
        fx = 0
        if exchange in [Exchange.HKSE]:
            # HKD to CNY
            fx_rate = data_provider.get_fx_quote_for_cny("HKD")
        elif exchange in [Exchange.NYSE, Exchange.NASDAQ]:
            # USD to CNY
            fx_rate = data_provider.get_fx_quote_for_cny("USD")
        elif exchange in [Exchange.OTC]:
            fx_rate = data_provider.get_fx_quote_for_cny(no_suffix_symbol)
        else:
            fx_rate = 1
        if fx_rate is not None:
            cny_net_value = net_value * fx_rate
            cny_margin_value = margin_value * fx_rate
        
        # Create new position history item
        PositionHistory.insert(symbol=curr_position.symbol,
                               exchange=curr_position.exchange,
                               volume=curr_position.volume,
                               platform=curr_position.platform,
                               pos_date=last_price_day,
                               run_date=today,
                               last_price=price,
                               net_value=net_value,
                               cny_net_value=cny_net_value,
                               margin_value=margin_value,
                               cny_margin_value=cny_margin_value).on_conflict_replace().execute()
                    
