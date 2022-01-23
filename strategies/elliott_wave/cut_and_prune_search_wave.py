import heapq
import time
import itertools
import wave_search_utils
import wave_utils
import waves
import logging

logger = logging.getLogger(__name__)

class CutAndPruneSearcher():
    def __init__(self, initial_point_list, additional_rules=[]):
        self.start_time = time.time()
        self.initial_point_list = initial_point_list
        self.optimum_point_list = wave_search_utils.get_all_local_optimum(initial_point_list)
        self.search_queue = []
        self.search_comb = []
        self.search_count = 0
        self.valid_wave_map = {}
        self.valid_wave_list = []
        self.additional_rules = additional_rules
        
        # 1. 以所有点的 index 作为第一个点，生成搜索组合加入队列
        for init_point_index in range(len(self.optimum_point_list)):
            for wave_type in wave_utils.get_all_concrete_subclass(waves.Wave):
                if issubclass(wave_type, waves.CombinationWave):
                    continue
                point_comb = wave_search_utils.PointComb((init_point_index,), wave_type, self.optimum_point_list)
                heapq.heappush(self.search_queue, point_comb)       
                self.search_comb.append(point_comb)
                
    def search_rest_comb(self):
        # 2. 根据 points limit，选取下一个随机点
        while len(self.search_queue) != 0:
            search_comb = heapq.heappop(self.search_queue)
            search_comb.update_next_point_limit(self.additional_rules)      

            for next_index in search_comb.get_next_available_points():
                index_list = search_comb.point_index_list + (next_index,)
                new_comb = wave_search_utils.PointComb(index_list, 
                                     search_comb.target_wave_type, 
                                     search_comb.original_points)
                # If already a wave
                if len(new_comb.point_index_list) == new_comb.target_wave_type.min_point_num:
                    wave = new_comb.get_wave()

                    if wave.is_valid():
                        self.valid_wave_map[search_comb.target_wave_type] = self.valid_wave_map.get(search_comb.target_wave_type, 0) + 1
                        self.valid_wave_list.append(wave)
                    else:
                        logger.debug(f"Invalid wave: {wave}")
                        for rule in wave.get_not_valid_rule():
                            logger.info("{0} {1}".format(rule, rule.desp))
                    continue
                
                heapq.heappush(self.search_queue, new_comb)
                self.search_count += 1
            if self.search_count % 10000 == 0:
                logger.debug(f"Already searched {self.search_count} combs")
                
    def add_point(new_point):
        # check optimum status, if same as previous point, replace the previous point
        
        
        # Create new point comb
        
        # Update point comb list
        
        # Push full wave
        
        pass
    
    def get_result(self):
        for wave_type, wave_num in self.valid_wave_map.items():
            logger.info(f"Found {wave_num} {wave_type}")
        logger.info(f"Total searched {self.search_count} combs, used time:" + str(time.time() - self.start_time))
        logger.info(f"Found valid wave {len(self.valid_wave_list)}")
        return self.valid_wave_list
    



            
