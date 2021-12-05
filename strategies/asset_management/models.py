from peewee import *

from vnpy.trader.database import get_database

class BaseModel(Model):
    class Meta:
        database = get_database().db
    
class PositionHistory(BaseModel):
    symbol = CharField()
    exchange = CharField()
    volume = IntegerField()
    platform = CharField()
    pos_date = DateField()

class CurrentPosition(BaseModel):
    symbol = CharField()
    exchange = CharField()
    volume = IntegerField()
    platform = CharField()
    updated_date = DateField()

class TargetPosition(BaseModel):
    symbol = CharField()
    exchange = CharField()
    volume = IntegerField()
    strategy = CharField()
    generate_date = DateField()
    
