from peewee import *

from vnpy.trader.database import get_database

class BaseModel(Model):
    class Meta:
        database = get_database().db
    
class PositionHistory(BaseModel):
    symbol = CharField()
    exchange = CharField()
    volume = DecimalField()
    platform = CharField()
    pos_date = DateField()
    # 价格
    last_price = DecimalField()
    # 净值
    net_value = DecimalField()
    # 保证金
    margin_value = DecimalField()
    
    class Meta:
        indexes = (
            (("symbol", "exchange", "pos_date"), True),
        )

class CurrentPosition(BaseModel):
    symbol = CharField()
    exchange = CharField()
    volume = DecimalField()
    platform = CharField()
    updated_date = DateField()

class TargetPosition(BaseModel):
    symbol = CharField()
    exchange = CharField()
    volume = DecimalField()
    strategy = CharField()
    generate_date = DateField()
    
class StrategyRunStatus(BaseModel):
    strategy = CharField()
    reason = TextField()
    status = CharField()
    run_time = IntegerField()
    run_date = DateField()
