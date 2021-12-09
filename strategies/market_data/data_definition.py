from vnpy.trader.constant import Exchange, Interval

from datetime import datetime, timedelta

class DataRequirement():
    interval = None
    
    def __init__(self, symbol, start_date, exchange):
        self.symbol = symbol
        self.start_date = start_date
        self.exchange = exchange
        
    def get_vnpy_symbol(self):
        return f"{self.symbol}.{self.exchange.value}"
    
class IndexData(DataRequirement):
    interval=Interval.DAILY
    
class FutureData(DataRequirement):
    interval=Interval.DAILY
    
    def get_monthly_symbol_list(self):
        current_date = self.start_date
        end_date = datetime.today()

        symbols = []
        
        while current_date < (end_date + timedelta(days=360)):
            current_date = (current_date + timedelta(days=32)).replace(day=1)
            date_str = current_date.strftime("%y%m")

            monthly_symbol = self.symbol + date_str
            symbols.append(f"{monthly_symbol}.{self.exchange.value}")
            
        return symbols
        
class FutureTickData(FutureData):
    """
        期货的日度价格数据
    """

        
class FutureHoldingData(FutureData):
    """
        期货的日度会员持仓数据
    """
    @property
    def long_open_chg_top20_field(self):
        return f"{self.symbol}_long_open_chg_top20"
    
    @property
    def long_open_chg_top20_symbol(self):
        return f"{self.long_open_chg_top20_field}.{self.exchange.value}"
   
    @property
    def short_open_chg_top20_field(self):
        return f"{self.symbol}_short_open_chg_top20"
    
    @property
    def short_open_chg_top20_symbol(self):
        return f"{self.short_open_chg_top20_field}.{self.exchange.value}"

class IndexTickData(DataRequirement):
    interval=Interval.DAILY
    
    def __init__(self, symbol, exchange, start_date):
        self.symbol = symbol
        self.exchange = exchange
        self.start_date = start_date
        
    
        
ic_daily_tick_data = FutureTickData(symbol="IC", start_date=datetime(2016,1,1), exchange=Exchange.CFFEX)
ic_holding_data = FutureHoldingData(symbol="IC", start_date=datetime(2016,1,1), exchange=Exchange.CFFEX)
ic_index_data = IndexData(symbol="000905", start_date=datetime(2016,1,1), exchange=Exchange.SSE)

if_daily_tick_data = FutureTickData(symbol="IF", start_date=datetime(2014,4,16), exchange=Exchange.CFFEX)
if_holding_data = FutureHoldingData(symbol="IF", start_date=datetime(2014,4,16), exchange=Exchange.CFFEX)
if_index_data = IndexData(symbol="000300", start_date=datetime(2014,4,16), exchange=Exchange.SSE)

cu_daily_tick_data = FutureTickData(symbol="CU", start_date=datetime(2010,1,1), exchange=Exchange.SHFE)
cu_holding_data = FutureHoldingData(symbol="CU", start_date=datetime(2010,1,1), exchange=Exchange.SHFE)

ih_daily_tick_data = FutureTickData(symbol="IH", start_date=datetime(2016,1,1), exchange=Exchange.CFFEX)
ih_holding_data = FutureHoldingData(symbol="IH", start_date=datetime(2016,1,1), exchange=Exchange.CFFEX)