from dataclasses import dataclass, field
import logging
import basic_types
import numpy as np

logger = logging.getLogger(__name__)

def get_all_local_optimum(point_list):
    local_optimum = []
    for index, point in enumerate(point_list):
        if index == 0 or index == len(point_list) - 1:
            local_optimum.append(point)
            continue
        if (point.price - point_list[index-1].price) * (point.price - point_list[index+1].price) < 0:
            continue
        if (point.price - point_list[index-1].price) > 0:
            point.optimum_type = basic_types.OptimumType.MAXIMUM
        else:
            point.optimum_type = basic_types.OptimumType.MINIMUM
        local_optimum.append(point)
    return local_optimum

def get_all_local_optimum_df(point_df):
    local_minimum_index = (point_df.shift(-1)["price"] > point_df["price"]) & (point_df.shift(1)["price"] > point_df["price"])
    local_maximum_index = (point_df.shift(-1)["price"] < point_df["price"]) & (point_df.shift(1)["price"] < point_df["price"])
    point_df["optimum_type"] = basic_types.OptimumType.UNKNOWN
    point_df["optimum_type"].loc[local_minimum_index] = basic_types.OptimumType.MINIMUM
    point_df["optimum_type"].loc[local_maximum_index] = basic_types.OptimumType.MAXIMUM
    local_optimum = point_df[point_df["optimum_type"] != basic_types.OptimumType.UNKNOWN]
    return local_optimum

def get_point_list_from_candle_dict_list(candle_dict_list):
    point_list = []
    first_date = candle_dict_list[0]["date"]
    for candle in candle_dict_list:
        curr_date = candle["date"]
        time_offset = (curr_date - first_date).days
        point_list.append(basic_types.Point(time_offset=time_offset, price=candle["close"], vol=candle["vol"]))
    return point_list

class PointLimit():
    def __init__(self):
        self.price_limit = (0, float('inf'))
        self.time_limit = (0, float('inf'))
        self.limit_func_list = []
        self.limit_source = {}
        
    def update_price_limit(self, new_limit):
        self.price_limit = (max(self.price_limit[0], new_limit[0]), 
                           min(self.price_limit[1], new_limit[1]))
        
    def update_time_limit(self, new_limit):
        self.time_limit = (max(self.time_limit[0], new_limit[0]), 
                           min(self.time_limit[1], new_limit[1]))

    def __str__(self):
        return str(self.price_limit) + str(self.time_limit) + str(self.limit_func_list) + str(self.limit_source)
        
    def point_fits_limit(self, point):
        if (point.price < self.price_limit[0] or point.price > self.price_limit[1]
            or point.time_offset < self.time_limit[0] or point.time_offset > self.time_limit[1]):
            return False
        for limit_func in self.limit_func_list:
            if not limit_func(point):
                return False
        return True
        
        
@dataclass(order=True)
class PointComb():
    priority = 0
    def __init__(self, init_point_index_list, target_wave_type, original_points):
        self.point_index_list = init_point_index_list
        self.original_points = original_points
        self.target_wave_type = target_wave_type
        self.next_point_limit = PointLimit()
    
    def get_wave(self):
        curr_point_list = [self.original_points[i] for i in self.point_index_list]
        return self.target_wave_type(curr_point_list)
    
    def update_next_point_limit(self, additional_rules=[]):
        """
        Use prev point comb and the rules to check next point imit
        """
        self.next_point_limit = PointLimit()
        curr_point_list = [self.original_points[i] for i in self.point_index_list]
        for rule in additional_rules:
            limit_map = rule.get_next_point_limit(self.target_wave_type, curr_point_list)
            if len(limit_map) == 0:
                continue
            self.next_point_limit.limit_func_list.append(limit_map["limit_func"])
        
        for rule in self.target_wave_type.rule_list:
            limit_map = rule.get_next_point_limit(curr_point_list)
            #logger.debug(f"Update next point limit for rule: {rule}, limit: {limit_map}")
            self.next_point_limit.limit_source[rule] = limit_map
            for limit_name, limit_value in limit_map.items():
                if limit_name == "price_limit":
                    self.next_point_limit.update_price_limit(limit_value)
                if limit_name == "time_limit":
                    self.next_point_limit.update_time_limit(limit_value)
                if limit_name == "limit_func":
                    self.next_point_limit.limit_func_list.append(limit_value)

    def get_next_available_points(self):
        """
        Check original points for available next points index
        """
        if len(self.point_index_list) == self.target_wave_type.min_point_num:
            return
        for index in range(self.point_index_list[-1]+1, len(self.original_points)):
            if self.next_point_limit.point_fits_limit(self.original_points[index]):
                yield index
            
                
def test_wave_next_point_limit_correctness(wave):
    for i in range(2, len(wave.point_list)):
        comb = PointComb(list(range(i)), type(wave), wave.point_list)
        comb.update_next_point_limit()
        next_point_list = list(comb.get_next_available_points())
        if i not in next_point_list:
            wave.show_line_chart()
            logger.error(f"Limit failed for {type(wave)}, i:{i}, point_list {wave.point_list}, next_point_limit {comb.next_point_limit}")
            return
        