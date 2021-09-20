from abc import ABC
import plotly.express as px
import pandas as pd
import json
import math

class NotValidWaveException(Exception):
    def __init__(self, Rule):
        self.Rule = Rule

    def __str__(self):
        return self.Rule.desp

class Point():
    def __init__(self, time_offset: int, price: float):
        self.time_offset = time_offset
        self.price = price
        
    def to_dict(self):
        return {
            'time_offset': self.time_offset,
            'price': self.price,
        }
    
    def __str__(self):
        return str(self.to_dict())
    
    def get_run_code(self):
        return f"Point({self.time_offset}, {self.price})"
        
class Wave(ABC):
    rule_list: list = [] #该类浪需要满足的规则列表
    guide_dict: dict = {} #该浪可以进行加权的指南以及权重
    min_point_num = 0 # 该浪最少应该有的点个数
    max_point_num = 999
    is_extend_wave = False # 是否是延长浪
    
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
        
    def get_sub_wave_type_limit(self):
        """
        子浪类型的可选值列表
        """
        return []
    
    def get_possible_subwave_combination(self):
        combinations = [[]]
        for wave_type_list in self.get_sub_wave_type_limit():
            new_combinations = []
            for wave_type in wave_type_list:
                for prev_comb in combinations:
                    new_combinations.append(prev_comb + [wave_type])
            combinations = new_combinations
        return combinations
    
    def init_subwave_with_types(self, subwave_types):
        self.sub_wave = [ subwave_type() for subwave_type in subwave_types ]
        
    def get_run_code(self):
        point_code_list = [ point.get_run_code() for point in self.point_list ]
        class_name = type(self).__name__
        return f"{class_name}([" + ",".join(point_code_list) + "])"
    
    def show_line_chart(self): 
        df = pd.DataFrame([x.to_dict() for x in self.point_list])
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
        

class Guide():
    desp = ""
    def get_score(wave:Wave):
        pass