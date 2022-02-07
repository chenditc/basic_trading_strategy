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
    hold_ratio = DecimalField(max_digits=50)
    class Meta:
        indexes = (
            (("symbol", "exchange", "ann_date", "end_date", "holder_name"), True),
         )
    
class StockBasicInfo(BaseModel):
    symbol = CharField()   # 股票代码
    exchange = CharField() # 交易所
    trade_date = DateField() # 日期
    turnover_rate = DecimalField(null = True) # 换手率（%）
    turnover_rate_f = DecimalField(null = True) # 换手率（自由流通股）
    volume_ratio = DecimalField(null = True) # 量比
    pe = DecimalField(null = True) # 市盈率（总市值/净利润， 亏损的PE为空）
    pe_ttm = DecimalField(null = True) # 市盈率（TTM，亏损的PE为空）
    pb = DecimalField(null = True) # 市净率（总市值/净资产）
    ps = DecimalField(null = True) # 市销率
    ps_ttm = DecimalField(null = True) # 市销率（TTM）
    dv_ratio = DecimalField(null = True) # 股息率 （%）
    dv_ttm = DecimalField(null = True) # 股息率（TTM）（%）
    total_share = DecimalField(null = True) # 总股本 （万股）
    float_share = DecimalField(null = True) # 流通股本 （万股）
    free_share = DecimalField(null = True) # 自由流通股本 （万）
    total_mv = DecimalField(null = True) # 总市值 （万元）
    circ_mv = DecimalField(null = True) # 流通市值（万元）
    
    class Meta:
        indexes = (
            (("symbol", "exchange", "trade_date"), True),
         )