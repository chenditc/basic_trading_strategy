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
    # 对应交易所币种的净值
    net_value = DecimalField(max_digits=50)
    # 人民币净值
    cny_net_value = DecimalField(max_digits=50)
    # 保证金
    margin_value = DecimalField(max_digits=50)
    # 人民币保证金
    cny_margin_value = DecimalField(max_digits=50)
    
    class Meta:
        indexes = (
            (("symbol", "exchange", "pos_date", "platform"), True),
        )

class CurrentPosition(BaseModel):
    symbol = CharField()
    name = CharField()
    tag1 = CharField()
    exchange = CharField()
    volume = DecimalField(max_digits=50)
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