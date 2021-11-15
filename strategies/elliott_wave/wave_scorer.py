from scipy import interpolate
import numpy as np
from collections import defaultdict

import wave_utils

class WaveScorer():     
    def __init__(self, original_point_list):
        self.original_point_list = original_point_list
        self.wave_score_map = {}
        self.wave_match_map = {}
        self.sub_wave_candidate_map = defaultdict(list)
        
        self.score_count = 0
        
        self.original_point_time_arr = np.array([p.time_offset for p in self.original_point_list])
        self.original_point_price_arr = np.array([p.price for p in self.original_point_list])

    def get_wave_key_from_wave(self, wave):
        key = "{}-{}-{}".format(wave.point_list[0].time_offset, 
                                wave.point_list[-1].time_offset,
                                str(type(wave).__name__))
        return key

    def get_wave_key(self, start_time, end_time, wave_type):
        key = "{}-{}-{}".format(start_time, 
                                end_time,
                                str(wave_type.__name__))
        return key
        
    def add_wave_as_parent_wave(self, new_wave):
        # 1. 生成子浪表。key - 父浪 
        wave_key = self.get_wave_key_from_wave(new_wave)
        wave_key_map = self.wave_match_map.get(wave_key, {"sub_wave": defaultdict(list), "parent_wave": []})
        wave_key_map["parent_wave"].append(new_wave)
        self.wave_match_map[wave_key] = wave_key_map
    
    def add_sub_wave_hunt(self, new_wave):
        # 2. 生成子浪表。key - 父浪
        # A two dimension list, first dim is subwave num, second dim is valid subwave
        sub_wave_limit = wave_utils.get_concrete_sub_wave_type_limit(new_wave)
        for subwave_num, concrete_subwave_type_list in enumerate(sub_wave_limit):
            for concrete_subwave_type in concrete_subwave_type_list:
                # TODO: if time is too short, don't need to add subwave hunt
                wave_key = self.get_wave_key(new_wave.point_list[subwave_num].time_offset,
                                        new_wave.point_list[subwave_num+1].time_offset,
                                        concrete_subwave_type)
                wave_key_map = self.wave_match_map.get(wave_key, {"sub_wave": defaultdict(list), "parent_wave": []})
                wave_key_map["sub_wave"][subwave_num].append(new_wave)
                self.wave_match_map[wave_key] = wave_key_map
                self.sub_wave_candidate_map[new_wave].append(wave_key_map)
                    
    def get_wave_score(self, new_wave):
        self.score_count += 1
        if self.score_count % 1000 == 0:
            print(f"Score count: {self.score_count}")
        
        score_info = new_wave.get_score_info()
        wave_total_time = (new_wave.point_list[-1].time_offset - new_wave.point_list[0].time_offset)
        wave_quality_score = score_info["min"] * wave_total_time

        target_points_index = ((self.original_point_time_arr >= new_wave.point_list[0].time_offset) & (self.original_point_time_arr <= new_wave.point_list[-1].time_offset))
        target_time_arr = self.original_point_time_arr[target_points_index]
        
        # calculate point correlation for wave.
        wave_point_time_arr = np.array([x.time_offset for x in new_wave.get_all_points()])
        wave_point_price_arr = np.array([x.price for x in new_wave.get_all_points()])
        wave_inter_line = interpolate.interp1d(wave_point_time_arr, wave_point_price_arr)

        wave_inter_points = wave_inter_line(target_time_arr)
        all_point_diff = sum(abs(wave_inter_points - self.original_point_price_arr[target_points_index]))
        
        # Calculate point correlation without subwave
        wave_point_time_arr = np.array([x.time_offset for x in new_wave.point_list])
        wave_point_price_arr = np.array([x.price for x in new_wave.point_list])
        wave_inter_line = interpolate.interp1d(wave_point_time_arr, wave_point_price_arr)

        wave_inter_points = wave_inter_line(target_time_arr)
        curr_point_diff = sum(abs(wave_inter_points - self.original_point_price_arr[target_points_index]))
        
        #print(f"Quality: {wave_quality_score}, point_diff: {point_diff}")
        final_score = wave_quality_score * (wave_total_time**2) / (all_point_diff + curr_point_diff + wave_total_time)
        return final_score  
    
    def update_wave_score(self, new_wave):
        self.wave_score_map[new_wave] = self.get_wave_score(new_wave)
        
    def update_all_wave_score(self):
        # Find all wave and update score. Wave which has sub wave hunt should be evaluate first, so that the wave hunting sub wave can leverage its subwave's score.
        # Use DFS so ensure that all wave will be updated from bottom up. This is a single directed graph.        
        def update_all_wave_score_helper(wave_to_update):
            # deduplicate
            if wave_to_update in self.wave_score_map:
                return
            
            for sub_wave_candidate_map in self.sub_wave_candidate_map[wave_to_update]:
                for sub_wave_candidate in sub_wave_candidate_map["parent_wave"]:
                    # Recursive update subwave score
                    update_all_wave_score_helper(sub_wave_candidate)
            # Pick best subwave comb
            self.search_and_update_max_sub_wave(wave_to_update)
            self.update_wave_score(wave_to_update)

        # Start with any wave and recursively update all wave
        for wave_key, wave_key_map in self.wave_match_map.items():
            if len(wave_key_map["parent_wave"]) == 0:
                continue
                
            for wave in wave_key_map["parent_wave"]:
                update_all_wave_score_helper(wave)
            
    def search_and_update_max_sub_wave(self, new_wave, only_subwave_num = None):
        # Check for all sub wave combination
        # TODO: Use combination score to help decide which wave to choose from
        sub_wave_limit = wave_utils.get_concrete_sub_wave_type_limit(new_wave)
        for subwave_num, concrete_subwave_type_list in enumerate(sub_wave_limit):
            if only_subwave_num and only_subwave_num != subwave_num:
                continue
            
            max_score_wave = None
            max_score = 0
            for concrete_subwave_type in concrete_subwave_type_list:
                wave_key = self.get_wave_key(new_wave.point_list[subwave_num].time_offset,
                                        new_wave.point_list[subwave_num+1].time_offset,
                                        concrete_subwave_type)
                # If no sub_wave exists, skip this sub_wave possibility
                wave_key_map = self.wave_match_map[wave_key]
                if len(wave_key_map["parent_wave"]) == 0:
                    continue
                
                max_score_wave = max(wave_key_map["parent_wave"], key=lambda x: self.wave_score_map[x])
                if max_score_wave != new_wave.sub_wave[subwave_num]:
                    new_wave.sub_wave[subwave_num] = max_score_wave
            
    def update_wave(self, new_wave):
        self.add_wave_as_parent_wave(new_wave)
        self.add_sub_wave_hunt(new_wave)