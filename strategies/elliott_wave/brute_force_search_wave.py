import wave_search_utils
import wave_utils
import itertools
import rules
import waves
import time
import logging

logger = logging.getLogger(__name__)

def get_points_combination(point_list, point_num):
    for point_comb in itertools.combinations(point_list, point_num):
        if rules.Rule0.validate_point_list(point_comb):
            yield point_comb

def brute_force_search_all_point_comb(input_point_list):
    start_time = time.time()

    optimum_point_list = wave_search_utils.get_all_local_optimum(input_point_list)
    result_wave_list = []

    logger.debug(f"Total points {len(optimum_point_list)}")
    search_count = 0
    for wave_type in wave_utils.get_all_concrete_subclass(waves.Wave):
        if issubclass(wave_type, waves.CombinationWave):
            continue
        logger.debug(f"Start search wave type: {wave_type}")

        valid_wave_num = 0
        point_num = wave_type.min_point_num
        for index, point_list in enumerate(get_points_combination(optimum_point_list, point_num)):
            search_count += 1
            if index % 100000 == 0 and index > 0:
                logger.debug(f"{wave_type} search progress: {index} found {valid_wave_num} valid wave")
            new_wave = wave_type(point_list)
            if not new_wave.is_valid():
                continue
            valid_wave_num += 1
            result_wave_list.append(new_wave)
        logger.info(f"Finished search {wave_type}, found {valid_wave_num}")

    logger.info(f"Total search count: {search_count} search time: " + str(time.time() - start_time))
    return result_wave_list