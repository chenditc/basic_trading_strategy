from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)

def get_all_local_optimum(point_list):
    local_optimum = []
    for index, point in enumerate(point_list):
        if index == 0 or index == len(point_list) - 1:
            local_optimum.append(point)
            continue
        if (point.price - point_list[index-1].price) * (point.price - point_list[index+1].price) < 0:
            continue
        local_optimum.append(point)
    return local_optimum

class PointLimit():
    def __init__(self):
        self.price_limit = (0, float('inf'))
        self.time_limit = (0, float('inf'))
        self.limit_func_list = []
        
    def update_price_limit(self, new_limit):
        self.price_limit = (max(self.price_limit[0], new_limit[0]), 
                           min(self.price_limit[1], new_limit[1]))
        
    def update_time_limit(self, new_limit):
        self.time_limit = (max(self.time_limit[0], new_limit[0]), 
                           min(self.time_limit[1], new_limit[1]))

    def __str__(self):
        return str(self.price_limit) + str(self.time_limit) + str(self.limit_func_list)
        
    def point_fits_limit(self, point):
        if (point.price > self.price_limit[0] and point.price < self.price_limit[1]
            and point.time_offset > self.time_limit[0] and point.time_offset < self.time_limit[1]):
            return True
        else:
            return False
        
        
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
    
    def update_next_point_limit(self):
        """
        Use prev point comb and the rules to check next point imit
        """
        self.next_point_limit = PointLimit()
        curr_point_list = [self.original_points[i] for i in self.point_index_list]
        for rule in self.target_wave_type.rule_list:
            limit_map = rule.get_next_point_limit(curr_point_list)
            logger.debug(f"Update next point limit for rule: {rule}, limit: {limit_map}")
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