import guides
import wave_utils
import waves
import rules
import basic_types
import datetime
import random

import plotly.graph_objects as go
import pandas as pd

def random_walk_between_points(start_point, end_point):
    time_range = end_point.time_offset - start_point.time_offset
    if time_range == 1:
        return [start_point, end_point]
    
    new_point_list = [start_point]
    for i in range(time_range-1):
        time_left = time_range - i
        step = (end_point.price - new_point_list[-1].price) / time_left
        next_price = new_point_list[-1].price + step*random.randint(5, 15)/10
        next_point = basic_types.Point(time_offset = start_point.time_offset + i +1, price=next_price)
        new_point_list.append(next_point)
    new_point_list.append(end_point)
    return new_point_list

def fill_points_with_random_walk(point_list):
    new_point_list = []
    for index, point in enumerate(point_list[:-1]):
        target_point = point_list[index+1]
        new_point_list += random_walk_between_points(point, target_point)[:-1]
    new_point_list.append(point_list[-1])
    return new_point_list

def convert_point_list_to_candle(point_list, start_date = datetime.datetime(2020, 1, 1)):
    candle_dict_list = [ ]
    for index, point in enumerate(point_list):
        prev_price = point_list[index-1].price if index > 0 else point.price
        price_list = [random.randint(-1500, 1500)/1000 * (prev_price - point.price) + point.price for i in range(3)]
        candle_dict_list.append({
            "date": start_date + datetime.timedelta(days=point.time_offset),
            "open": price_list[0],
            "close": point.price,
            "high" : max(point.price, max(price_list)),
            "low": min(point.price, min(price_list)),
            "vol": point.price,
        })
    return candle_dict_list

def generate_random_wave(wave_type, max_time=60, first_price=1000, last_price=3000, show_chart=False):
    base_wave = wave_utils.find_wave_for_scale(wave_type, 
                                   min_time=0, 
                                   max_time=max_time, 
                                   first_price=first_price, 
                                   last_price=last_price, 
                                   try_times=200, 
                                   show_chart=False)
    if show_chart:
        base_wave.show_line_chart()

    wave_utils.expand_sub_wave_to_points(base_wave)
    if show_chart:
        base_wave.show_line_chart()

    filled_points = fill_points_with_random_walk(base_wave.get_all_points())
    candle_dict_list = convert_point_list_to_candle(filled_points)

    if show_chart:
        df = pd.DataFrame(candle_dict_list)
        fig = go.Figure(data=[go.Candlestick(x=df['date'],
                        open=df['open'],
                        high=df['high'],
                        low=df['low'],
                        close=df['close'])])
        fig.show()
    return candle_dict_list