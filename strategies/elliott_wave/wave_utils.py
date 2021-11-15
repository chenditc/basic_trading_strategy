import math
import rules
import random
import waves
import time
import basic_types
from pathlib import Path
from copy import copy
import os
import json
import numpy as np

def load_wave_from_dict(wave_dict):
    if wave_dict is None:
        return None
    wave_type = wave_dict["type"]
    module = __import__("waves")
    wave_cls = getattr(module, wave_type, None)
    if wave_cls is None:
        raise Exception("Unknown wave type" + wave_type)
    wave_obj = wave_cls()
    wave_obj.point_list = [ basic_types.Point(**point_dict) for point_dict in wave_dict["points"] ]
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

def get_poly_line_by_point(p1, p2):
    return np.poly1d(np.polyfit(
        [p1.time_offset, p2.time_offset],
        [p1.price, p2.price],
        deg=1))

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
     
def get_all_concrete_subclass(wave_type):
    concrete_class_list = []
    if wave_type.is_concrete_wave:
        concrete_class_list.append(wave_type)
    
    sub_class_list = wave_type.__subclasses__()
    for sub_class in sub_class_list:
        if sub_class.is_concrete_wave:
            concrete_class_list.append(sub_class)
        concrete_class_list += get_all_concrete_subclass(sub_class)
    result = list(set(concrete_class_list))
    return result

def expand_wave_type_to_concrete(wave_type_list):
    result = []
    for wave_type in wave_type_list:
        result += get_all_concrete_subclass(wave_type)
    return list(set(result))

wave_combination_cache = {}
def get_possible_subwave_combination(wave_type):
    if wave_type in wave_combination_cache:
        return wave_combination_cache[wave_type]
    combinations = [[]]
    temp_wave = wave_type()
    for wave_type_list in wave_type.get_sub_wave_type_limit():
        new_combinations = []
        expanded_wave_type_list = expand_wave_type_to_concrete(wave_type_list)
        for sub_wave_type in expanded_wave_type_list:
            for prev_comb in combinations:
                new_combinations.append(prev_comb + [sub_wave_type])
        combinations = new_combinations
    # Filter by rule
    valid_comb = []
    for combination in combinations:
        temp_wave.sub_wave = [ sub_wave_type() for sub_wave_type in combination]
        invalid_comb = False
        for rule in temp_wave.rule_list:
            if issubclass(rule, rules.SubWaveRule) and not rule.validate(temp_wave):
                invalid_comb = True
                break
        if invalid_comb:
            continue
        valid_comb.append(combination)
    
    wave_combination_cache[wave_type] = valid_comb
    return valid_comb

def generate_random_points(point_num, time_offset_list, price_list):
    # pick n time
    time_list = sorted(random.sample(time_offset_list, point_num))
    # pick n price
    price_list = random.sample(price_list, point_num)
    point_list = [ basic_types.Point(time_offset, price) for time_offset, price in zip(time_list, price_list)]
    return point_list

def find_matching_wave_for_guide(target_guide, target_score, target_wave_type, wave_size = 20, iteration=50000):
    min_rules_wave = None
    min_rules_num = 100
    print(target_wave_type.rule_list)
    for i in range(iteration):
        wave_point_num = random.randint(target_wave_type.min_point_num, target_wave_type.max_point_num)
        point_list = generate_random_points(point_num=wave_point_num, 
                                            time_offset_list=list(range(wave_size)),
                                            price_list=list(range(100, 100+wave_size)))
        wave = target_wave_type(point_list)
        wave.sub_wave[2] = waves.ExtendImpluseWave()
        if not wave.is_valid():
            continue
        if target_guide.get_score(wave) != target_score:
            continue
        wave.show_line_chart()
        score_reason_dict = wave.get_score_contribution()
        print(wave_utils.get_run_code_for_wave(wave))
        for score_reason, score in score_reason_dict.items():
            print(score, score_reason)
        break
    print("Not finding anything")
    
def generate_test_case_for_rule(rule,
                                target_wave_type, 
                                 wave_size = 10,
                                 iteration=50000):
    print(target_wave_type.rule_list)
    min_rules_wave = None
    min_rules_num = 100
    for i in range(iteration):
        wave_point_num = random.randint(target_wave_type.min_point_num, target_wave_type.max_point_num)
        
        point_list = generate_random_points(point_num=wave_point_num, 
                                            time_offset_list=list(range(wave_size)),
                                            price_list=list(range(100, 100+wave_size)))
        wave = target_wave_type(point_list)

        if not wave.is_valid():
            rules = wave.get_not_valid_rule()
            if rule in rules:
                if len(rules) < min_rules_num:
                    min_rules_num = len(rules)
                    min_rules_wave = wave
            
    min_rules_wave.show_line_chart()
    print(rule.desp)
    print(wave_utils.get_run_code_for_wave(min_rules_wave))

def get_most_possible_subwave_combination(wave):
    """
    根据该浪可能有的子浪类型，计算添加子浪形态后，符合规则且分数最高的子浪形态组合列表
    """
    combinations = get_possible_subwave_combination(type(wave))
    max_score = 0
    max_score_list = []
    for combination in combinations:
        wave.init_subwave_with_types(combination)
        score = wave.get_score()
        if score > max_score:
            max_score = score
            max_score_list = []
        if score == max_score:
            max_score_list.append(combination)
    return(max_score, max_score_list)

def generate_wave_point_list(target_wave_type, 
                             wave_size = 20,
                             iteration=50000,
                             total_wave_num=50,
                             time_limit=30):
    assert(len(target_wave_type.rule_list) > 0)
    start_time = time.time()
    
    max_score = -1
    max_score_wave_list = []
    for i in range(iteration):
        if time.time() > start_time + time_limit:
            break
        wave_point_num = random.randint(target_wave_type.min_point_num, target_wave_type.max_point_num)
        
        point_list = generate_random_points(point_num=wave_point_num, 
                                            time_offset_list=list(range(wave_size)),
                                            price_list=list(range(100, 100+wave_size)))
        wave = target_wave_type(point_list)
        if not wave.is_valid():
            continue            
        wave_score = wave.get_score()
        
        sub_wave_score, sub_wave_comb_list = get_most_possible_subwave_combination(wave)
        wave.init_subwave_with_types(sub_wave_comb_list[0])
        if sub_wave_score < max_score:
            continue        
        if sub_wave_score > max_score:
            max_score = sub_wave_score
            max_score_wave_list = []
        if len(max_score_wave_list) > total_wave_num:
            continue
        max_score_wave_list.append(wave)
    return max_score, max_score_wave_list

def save_wave_json_to_file(wave, file_path):
    json_str = wave.to_json(indent=2)
    with open(file_path, "w") as output_file:
        print("Saving wave to file {}".format(file_path))
        output_file.write(json_str)

def print_wave_info(wave):
    wave.show_line_chart()
    print(get_run_code_for_wave(wave))
    score_reason_dict = wave.get_score_contribution()
    for score_reason, score in score_reason_dict.items():
        print(score, score_reason)
        
def generate_and_save_max_score_wave(target_wave_type, 
                                     wave_size=20,
                                     iteration=50000,
                                     total_wave_num=50,
                                     time_limit=30):
    max_score, max_score_wave_list = generate_wave_point_list(target_wave_type = target_wave_type, wave_size=wave_size, iteration=iteration, time_limit=time_limit)
    print(f"Max score is {max_score}")
    target_directory = "sample_waves/{0}/{1}".format(target_wave_type.__name__, max_score)
    Path(target_directory).mkdir(parents=True, exist_ok=True)
    for index, wave in enumerate(max_score_wave_list[:total_wave_num]):
        print_wave_info(wave)
        target_file_path = "{0}/{1}.json".format(target_directory, index)
        save_wave_json_to_file(wave, target_file_path)
        
def generate_from_sample_wave(target_wave_type):
    sample_wave_score_list_path = f"sample_waves/{target_wave_type.__name__}/"
    sample_wave_score_list = [int(x) for x in os.listdir(sample_wave_score_list_path)]
    max_score = max(sample_wave_score_list)
    sample_file_dir = f"sample_waves/{target_wave_type.__name__}/{max_score}/"
    sample_file_list = os.listdir(sample_file_dir)
    picked_file = random.choice(sample_file_list)
    
    with open(sample_file_dir + picked_file, "r") as wave_json_file:
        return json.loads(wave_json_file.read())

def scale_wave_to_time_and_price(wave, min_time, max_time, first_price, last_price):
    new_point_list = []
    base_time = wave.point_list[0].time_offset
    base_price = wave.point_list[0].price
    time_scale = (max_time - min_time) / (wave.point_list[-1].time_offset - base_time)
    price_scale = (last_price - first_price) / (wave.point_list[-1].price - base_price)
    
    for point in wave.point_list:
        new_time_offset = (point.time_offset - base_time) * time_scale + min_time
        new_price = (point.price - base_price) * price_scale + first_price
        point.price = new_price
        point.time_offset = int(new_time_offset)

        
def find_wave_for_scale(wave_type, min_time, max_time, first_price, last_price, try_times=200, show_chart=True):
    for i in range(try_times):
        wave_dict = generate_from_sample_wave(wave_type)
        wave = load_wave_from_dict(wave_dict)
        if show_chart:
            wave.show_line_chart()

        scale_wave_to_time_and_price(wave, min_time, max_time, first_price, last_price)
        if show_chart:
            wave.show_line_chart()
        if not wave.is_valid():
            continue
        return wave

def expand_sub_wave_to_points(base_wave):
    for index in range(1, len(base_wave.point_list)):
        start_point = base_wave.point_list[index-1]
        end_point = base_wave.point_list[index]
        new_sub_wave = find_wave_for_scale(type(base_wave.sub_wave[index-1]), 
                                           min_time=start_point.time_offset, 
                                           max_time=end_point.time_offset,
                                           first_price=start_point.price,
                                           last_price=end_point.price, 
                                           try_times=20,
                                           show_chart=False)
        if new_sub_wave:
            base_wave.sub_wave[index-1] = new_sub_wave
            if new_sub_wave.point_list[-1].time_offset - new_sub_wave.point_list[0].time_offset > 4:
                expand_sub_wave_to_points(new_sub_wave)
                
def get_concrete_sub_wave_type_limit(wave):
    if hasattr(wave.__class__, "concrete_sub_wave_type_limit"):
        return wave.__class__.concrete_sub_wave_type_limit

    
    sub_wave_limit = wave.__class__.get_sub_wave_type_limit()
    concrete_sub_wave_type_limit = []
    for subwave_num in range(len(sub_wave_limit)):
        concrete_sub_wave_type_limit.append([])
        for abstract_type in sub_wave_limit[subwave_num]:
            concrete_subwave_type_list = get_all_concrete_subclass(abstract_type)
            concrete_sub_wave_type_limit[subwave_num] += concrete_subwave_type_list

    wave.__class__.concrete_sub_wave_type_limit = concrete_sub_wave_type_limit
    return concrete_sub_wave_type_limit
     