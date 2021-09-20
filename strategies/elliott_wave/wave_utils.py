from basic_types import *
import math
from waves import *

def load_wave_from_dict(wave_dict):
    if wave_dict is None:
        return None
    wave_type = wave_dict["type"]
    module = __import__("waves")
    wave_cls = getattr(module, wave_type, None)
    if wave_cls is None:
        raise Exception("Unknown wave type" + wave_type)
    wave_obj = wave_cls()
    wave_obj.point_list = [ Point(**point_dict) for point_dict in wave_dict["points"] ]
    wave_obj.sub_wave = [ load_wave_from_dict(sub_wave_dict) 
                         for sub_wave_dict in wave_dict["sub_wave"]]
    return wave_obj

def get_run_code_for_wave(wave):
    return "wave_utils.load_wave_from_dict({0})".format(wave.to_dict())

def get_wave_moving_ratio(p1, p2):
    """
    计算两个子浪的终点连线的斜率，价格变化使用百分比计数，也就是对数刻度。
    """
    time_diff = p2.time_offset - p1.time_offset
    price_change = math.log(p2.price) - math.log(p1.price)
    ratio = price_change / time_diff
    return ratio

def find_intersection(x1,y1,x2,y2,x3,y3,x4,y4):
    try:
        px= ( (x1*y2-y1*x2)*(x3-x4)-(x1-x2)*(x3*y4-y3*x4) ) / ( (x1-x2)*(y3-y4)-(y1-y2)*(x3-x4) ) 
        py= ( (x1*y2-y1*x2)*(y3-y4)-(y1-y2)*(x3*y4-y3*x4) ) / ( (x1-x2)*(y3-y4)-(y1-y2)*(x3-x4) )
        return [px, py]
    except ZeroDivisionError as e:
        return [None, None]

def get_points_line_converge_point(line1_p1, line1_p2, line2_p1, line2_p2):
    time_offset, price = find_intersection(
        line1_p1.time_offset, math.log(line1_p1.price),
        line1_p2.time_offset, math.log(line1_p2.price),
        line2_p1.time_offset, math.log(line2_p1.price),
        line2_p2.time_offset, math.log(line2_p2.price),
    )
    return (time_offset, math.exp(price))

def get_line_extend_point(point1, point2, time):
    ratio = (math.log(point1.price) - math.log(point2.price)) / (point1.time_offset - point2.time_offset)
    log_price = (time - point2.time_offset) * ratio + math.log(point2.price)
    return math.exp(log_price)

def value_close_to(test_value, target_value, diff_ratio):
    if target_value != 0:
        return ((test_value - target_value) / target_value) < diff_ratio
    elif test_value != 0:
        return ((test_value - target_value) / test_value) < diff_ratio
    else:
        return True
     