import heapq
import time
import itertools
import wave_search_utils
import wave_utils
import waves
import logging

logger = logging.getLogger(__name__)

def cut_and_prune_search_wave(input_point_list, additional_rules=[]):
    start_time = time.time()
   
    optimum_point_list = wave_search_utils.get_all_local_optimum(input_point_list)
    search_queue = []
    search_count = 0
    # 1. 以所有点的 index 作为第一个点，生成搜索组合加入队列
    for init_point_index in range(len(optimum_point_list)):
        for wave_type in wave_utils.get_all_concrete_subclass(waves.Wave):
            if issubclass(wave_type, waves.CombinationWave):
                continue
            heapq.heappush(search_queue, wave_search_utils.PointComb((init_point_index,), wave_type, optimum_point_list))
            search_count += 1

    # 2. 根据 points limit，选取下一个随机点
    valid_wave_map = {}
    valid_wave_list = []
    while len(search_queue) != 0:
        search_comb = heapq.heappop(search_queue)
        if len(search_comb.point_index_list) == search_comb.target_wave_type.min_point_num:
            wave = search_comb.get_wave()
                    
            if wave.is_valid():
                valid_wave_map[search_comb.target_wave_type] = valid_wave_map.get(search_comb.target_wave_type, 0) + 1
                valid_wave_list.append(wave)
            else:
                logger.debug(f"Invalid wave: {wave}")
                for rule in wave.get_not_valid_rule():
                    logger.info("{0} {1}".format(rule, rule.desp))
            continue

        search_comb.update_next_point_limit(additional_rules)      
        
        for next_index in search_comb.get_next_available_points():
            index_list = search_comb.point_index_list + (next_index,)
            new_comb = wave_search_utils.PointComb(index_list, 
                                 search_comb.target_wave_type, 
                                 search_comb.original_points)
            heapq.heappush(search_queue, new_comb)
            search_count += 1
        if search_count % 10000 == 0:
            logger.debug(f"Already searched {search_count} combs")
            
    for wave_type, wave_num in valid_wave_map.items():
        logger.info(f"Found {wave_num} {wave_type}")
    logger.info(f"Total searched {search_count} combs, used time:" + str(time.time() - start_time))
    logger.info(f"Found valid wave {len(valid_wave_list)}")
    return valid_wave_list