from peewee import *

from vnpy.trader.database import get_database

class BaseModel(Model):
    class Meta:
        database = get_database().db

class FutureInfo(BaseModel):
    future_symbol = CharField()
    margin_rate = DecimalField()
    multiplier = DecimalField()
    priceticks = DecimalField()
    
class FutureHoldingData(BaseModel):
    trade_date = DateField()
    symbol = CharField()
    exchange = CharField()
    broker = CharField()
    vol = DecimalField(null = True)
    vol_chg = DecimalField(null = True)
    long_hld = DecimalField(null = True)
    long_chg = DecimalField(null = True)
    short_hld = DecimalField(null = True)
    short_chg = DecimalField(null = True)
    
    class Meta:
        indexes = (
            (("trade_date", "symbol", "exchange", "broker"), True),
         )

class StockIndexWeightData(BaseModel):
    index_symbol = CharField()   # 指数代码
    index_exchange = CharField() # 指数交易所
    stock_symbol = CharField()   # 股票代码
    stock_exchange = CharField() # 股票交易所
    trade_date = DateField()
    weight = DecimalField()   # 权重
    
    class Meta:
        indexes = (
            (("trade_date", "index_symbol", "index_exchange", "stock_symbol", "stock_exchange"), True),
         )
        
class StockHoldingData(BaseModel):
    symbol = CharField()   # 股票代码
    exchange = CharField() # 交易所
    ann_date = DateField() # 公告发布日期
    end_date = DateField() # 报告结束日期
    holder_name = CharField()
    hold_amount = DecimalField(max_digits=50)