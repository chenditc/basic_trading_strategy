from abc import ABC
import plotly.express as px
import pandas as pd
import json
import math
import copy

from enum import Enum
class OptimumType(Enum):
    UNKNOWN = 0
    MAXIMUM = 1
    MINIMUM = 2

class NotValidWaveException(Exception):
    def __init__(self, Rule):
        self.Rule = Rule

    def __str__(self):
        return self.Rule.desp

class Point():
    def __init__(self, time_offset: int, price: float, vol: int=0, optimum_type=OptimumType.UNKNOWN):
        self.time_offset = time_offset
        self.price = price
        self.vol = vol
        self.optimum_type = optimum_type
        
    @classmethod
    def from_dict(cls, input_dict):
        return cls(**input_dict)
        
    def to_dict(self):
        return {
            'time_offset': self.time_offset,
            'price': self.price,
            'vol': self.vol,
            'optimum': self.optimum_type
        }
    
    def __str__(self):
        return str(self.to_dict())
    
    def __repr__(self):
        return str(self.to_dict())
    
    def get_run_code(self):
        return f"Point({self.time_offset}, {self.price}, {self.vol})"
        
class Wave(ABC):
    rule_list: list = [] #该类浪需要满足的规则列表
    guide_dict: dict = {} #该浪可以进行加权的指南以及权重
    min_point_num = 0 # 该浪最少应该有的点个数
    max_point_num = 999
    is_extend_wave = False # 是否是延长浪
    is_concrete_wave = False
    max_guide_score = 1
    
    def __init__(self, point_list: list = [], sub_wave_types = []):
        self.point_list = point_list
        # 子浪序列，初始为 None
        sub_wave_num = max(0, len(point_list) -1)
        self.sub_wave: list[Wave] = [None] * sub_wave_num
    
    @property
    def first_sub_wave_trend(self):
        """
        第一个子浪的方向，1为向上，0为向下
        """
        if len(self.point_list) < 2:
            return 0
        if self.point_list[0].price < self.point_list[1].price:
            return 1
        return 0
        
    def init_subwave_with_types(self, subwave_types):
        self.sub_wave = [ subwave_type() for subwave_type in subwave_types ]
        
    def get_run_code(self):
        point_code_list = [ point.get_run_code() for point in self.point_list ]
        class_name = type(self).__name__
        return f"{class_name}([" + ",".join(point_code_list) + "])"
    
    def get_all_points(self):
        """
            获取所有点，包括子浪的
        """
        point_list = copy.copy(self.point_list)
        for sub_wave in self.sub_wave:
            if sub_wave:
                point_list += sub_wave.get_all_points()[1:-1]
        sorted_list = sorted(point_list, key=lambda x: x.time_offset)
        return sorted_list
    
    def show_line_chart(self): 
        df = pd.DataFrame([x.to_dict() for x in self.get_all_points()])
        fig = px.line(df, x="time_offset", y="price", title='wave')
        fig.update_layout(updatemenus = list([
            dict(active=1,
                 buttons=list([
                    dict(label='Log Scale',
                         method='update',
                         args=[{'visible': [True, True]},
                               {'title': 'Log scale',
                                'yaxis': {'type': 'log'}}]),
                    dict(label='Linear Scale',
                         method='update',
                         args=[{'visible': [True, False]},
                               {'title': 'Linear scale',
                                'yaxis': {'type': 'linear'}}])
                    ]),
                )
            ])
        )
        fig.show()
    
    def to_dict(self):
        result = {
            "type" : self.__class__.__name__,
            "points" : [ point.to_dict() for point in self.point_list ],
            "sub_wave": []
        }
        for sub_wave in self.sub_wave:
            if sub_wave:
                result["sub_wave"].append(sub_wave.to_dict())
            else:
                result["sub_wave"].append(sub_wave)
        return result
    
    def to_json(self, indent=None):
        return json.dumps(self.to_dict(), indent=indent)
    
    def sub_wave_is_extend(self, sub_wave_num):
        sub_wave = self.sub_wave[sub_wave_num]
        if sub_wave and sub_wave.is_extend_wave:
            return True
        return False
    
    def is_valid(self):
        """
        看是否符合该浪的定义
        """
        for rule in self.rule_list:
            result = rule.validate(self)
            if not result:
                return False
        return True
    
    def get_not_valid_rule(self):
        result = []
        for rule in self.rule_list:
            if not rule.validate(self):
                result.append(rule)
        return result
    
    def set_sub_wave(self, sub_wave_num, sub_wave):
        self.sub_wave[sub_wave_num] = sub_wave
            
    def get_score(self):
        """
        看当前的浪分布满足多少指南
        """
        total_score = 0
        for guide, weight in self.guide_dict.items():
            total_score += weight * guide.get_score(self)
        return total_score
    
    def get_score_info(self):
        total_score_info = {
            "min" : 0,
            "max" : 0,
            "improve_sub_wave_type" : []
        }
        for guide, weight in self.guide_dict.items():
            curr_score_info = guide.get_score_info(self)
            total_score_info["min"] += curr_score_info["min"]
            total_score_info["max"] += curr_score_info["max"]
            total_score_info["improve_sub_wave_type"] += curr_score_info["improve_sub_wave_type"]
        
        return total_score_info
    
    def get_score_contribution(self):
        """
        看当前的浪分布满足指南的列表
        """
        score_reason = {}
        for guide, weight in self.guide_dict.items():
            score_reason[guide.desp] = weight * guide.get_score(self)
        return score_reason
    
    def get_sub_wave_time(self, sub_wave_num):
        return self.point_list[sub_wave_num+1].time_offset - self.point_list[sub_wave_num].time_offset
    
    def get_sub_wave_move(self, sub_wave_num):
        return math.log(self.point_list[sub_wave_num+1].price) - math.log(self.point_list[sub_wave_num].price)

    def get_sub_wave_move_abs(self, sub_wave_num):
        return abs(self.get_sub_wave_move(sub_wave_num))

class Rule():
    desp = ""
    def validate(wave: Wave):
        raise NotImplementedError
        
    def get_next_point_limit(point_list):
        """
        get a map of point limit
        """
        return {}

class Guide():
    desp = ""
    @classmethod
    def get_score(cls, wave:Wave):
        pass
    
    @classmethod
    def get_score_info(cls, wave: Wave):
        curr_score = cls.get_score(wave)
        score_info = {
            "min" : curr_score,
            "max" : curr_score,
            "improve_sub_wave_type": []
        }
        return score_info