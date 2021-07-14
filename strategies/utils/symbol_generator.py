from datetime import datetime, timedelta

def get_index_future_symbol(start_date, end_date, prefix = "IC"):
    current_date = start_date
    
    symbols = []

    while current_date < (end_date + timedelta(days=360)):
        current_date = (current_date + timedelta(days=32)).replace(day=1)
        date_str = current_date.strftime("%y%m")

        ts_code = prefix + date_str
        symbols.append(ts_code)
    return symbols
       
