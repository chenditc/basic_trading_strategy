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