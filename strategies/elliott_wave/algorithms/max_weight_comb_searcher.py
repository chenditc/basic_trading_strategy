import bisect

class MaxWeightCombSearcher():
    def __init__(self, get_start_time, get_end_time, get_weight):
        self.input_wave_list = []
        self.search_result_list = []
        
        self.curr_max_result = ([], -1)
        self.last_search_index = -1
        
        self.get_start_time = get_start_time
        self.get_end_time = get_end_time
        self.get_weight = get_weight
        
    def add_new_waves_list(self, new_wave_list, reset_progress=False):
        self.input_wave_list += sorted(new_wave_list, key=self.get_end_time)
        self.search_result_list += [None] * len(new_wave_list)
        
        if reset_progress:
            self.last_search_index = -1
            self.input_wave_list = sorted(self.input_wave_list, key=self.get_end_time)
            self.search_result_list = [None] * len(self.input_wave_list)
            self.curr_max_result = ([], -1)
        
    def find_max_weight_comb(self):
        end_time_list = [self.get_end_time(x) for x in self.input_wave_list]
        for i in range(self.last_search_index+1, len(self.input_wave_list)):
            start_time = self.get_start_time(self.input_wave_list[i])
            non_overlap_index = bisect.bisect_right(end_time_list, start_time)
            if non_overlap_index == 0:
                # 找不到在当前元素之self.input_wave_list前，且不重叠的元素组合，则使用当前元素自己的权重值。
                new_result = ([self.input_wave_list[i]], self.get_weight(self.input_wave_list[i]))
            else:
                # 可以找到在当前元素之前，并且不重叠的元素最大加权调度组合，则把当前元素加到之前的组合里，并记录下权重值。
                new_result = (self.search_result_list[non_overlap_index-1][0] + [self.input_wave_list[i]], 
                              self.search_result_list[non_overlap_index-1][1] + self.get_weight(self.input_wave_list[i]))
            
            # 将这个权重值与之前已记录的最大权重值进行比较，如果更大，则更新进当前的权重组合中，否则使用之前的权重组合和最大权重值。
            if new_result[1] > self.curr_max_result[1]:
                self.curr_max_result = new_result
                self.search_result_list[i] = new_result
            else:
                self.search_result_list[i] = self.curr_max_result
                
            self.last_search_index = i