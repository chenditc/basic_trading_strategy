from vnpy.trader.database import get_database
from peewee import OperationalError
import time

def connect_db_and_wait(seconds=20):
    for i in range(seconds):
        try:
            db = get_database()
            print("Created connection")
            break
        except OperationalError as e:
            print("Wait and retrying for error", e)
            time.sleep(1)