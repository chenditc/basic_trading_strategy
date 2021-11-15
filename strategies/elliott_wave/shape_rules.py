import numpy as np
import waves
import basic_types
from scipy.spatial import ConvexHull

class ShapeRule1():
    desp = "如果子浪只包括推动浪或锯齿调整浪，那么该子浪区间不会点超过浪的起点和终点所框的正方形"
    wave_target_cache = {}
    
    def __init__(self, all_points_df):
        self.all_points_df = all_points_df
    
    def get_time_offset_limit_func(self, valid_time_offset_set):
        def next_point_is_in_valid_set(next_point, *args, **kargs):
            return (next_point.time_offset in valid_time_offset_set)
        return next_point_is_in_valid_set
    
    @classmethod
    def get_only_increase_subwave_num(cls, wave_type):
        if wave_type not in cls.wave_target_cache:
            only_increase_subwave_num = []
            sub_wave_limit = wave_type.get_sub_wave_type_limit()
            for subwave_num, concrete_subwave_type_list in enumerate(sub_wave_limit):
                # 子浪只包括推动浪或锯齿调整浪
                only_increase = all([(issubclass(subwave_type, waves.ZigZagWave) or issubclass(subwave_type, waves.MotiveWave)) for subwave_type in concrete_subwave_type_list])
                if only_increase:
                    only_increase_subwave_num.append(subwave_num)

            cls.wave_target_cache[wave_type] = only_increase_subwave_num
        return cls.wave_target_cache[wave_type]
    
    def validate(self, wave):
        wave_type = type(wave)
        for subwave_num in self.get_only_increase_subwave_num(wave_type):
            valid_range = sorted([wave.point_list[subwave_num].price, wave.point_list[subwave_num+1].price])
            target_time_range = sorted([wave.point_list[subwave_num].time_offset, wave.point_list[subwave_num+1].time_offset])
            
            target_points = self.all_points_df.loc[target_time_range[0]:target_time_range[1]]
            for price in target_points["price"]:
                if price < valid_range[0] or price > valid_range[1]:
                    #print(f"Subwave num: {subwave_num}, valid range: {valid_range}, {wave.point_list[subwave_num]}")
                    #show_wave_point_in_original_line(wave, chosen_point_list)
                    return False
            
        return True
    
    def get_next_point_limit(self, wave_type, point_list):
        limit_map = {}
        next_sub_wave_num = len(point_list) - 1
        if next_sub_wave_num not in self.get_only_increase_subwave_num(wave_type):
            return limit_map                                    
        
        # Next point should be accumulative max or min
        target_points = self.all_points_df.loc[point_list[-1].time_offset:]
        accumulate_min = np.minimum.accumulate(target_points["price"])
        accumulate_max = np.maximum.accumulate(target_points["price"])
        if point_list[-1].optimum_type == basic_types.OptimumType.MAXIMUM:
            # Find accumulative minimum, also, accumulate maximum should be smaller than curr point
            result = target_points[(target_points["price"] == accumulate_min) & (accumulate_max <= point_list[-1].price)]
        elif point_list[-1].optimum_type == basic_types.OptimumType.MINIMUM:
            # Find accumulative maximum
            result = target_points[(target_points["price"] == accumulate_max) & (accumulate_min >= point_list[-1].price)]
        else:
            return limit_map
        limit_map["limit_func"] = self.get_time_offset_limit_func(set(result["time_offset"]))
        return limit_map
    
class ShapeRule2():
    desp = "如果子浪是三角浪或平台浪，那么子浪中的点最大值和最小值应当在浪峰、浪谷的连线范围内。"

    def __init__(self, all_points_df):
        self.all_points_df = all_points_df
    
    def get_wave_barrier_limit_func(self, remaining_points_result):
        def next_point_is_within_hull(next_point, *args, **kargs):
            return next_point.time_offset in remaining_points_result
        return next_point_is_within_hull
    
    def validate(self, wave):
        wave_type = type(wave)
        if issubclass(wave_type, waves.TriangleWave):
            # 浪1、3 终点连线
            line1_3 = wave_utils.get_poly_line_by_point(wave.point_list[1], wave.point_list[3])
            # 浪2、4终点连线
            line2_4 = wave_utils.get_poly_line_by_point(wave.point_list[2], wave.point_list[4])
        
            target_points = self.all_points_df.loc[wave.point_list[1].time_offset:wave.point_list[4].time_offset]
            for point in target_points["point"]:
                diff1 = point.price - line1_3(point.time_offset)
                diff2 = point.price - line2_4(point.time_offset)
                if abs(diff1) < 0.01 or abs(diff2) < 0.01:
                    continue
                if diff1 * diff2 > 0:
                    #print(point.price,  line1_3(point.time_offset), line2_4(point.time_offset))
                    return False
                
        if issubclass(wave_type, waves.FlatWave):
            # 浪1、3 终点连线
            line1_3 = wave_utils.get_poly_line_by_point(wave.point_list[1], wave.point_list[3])
            # 浪1、3 起点连线
            line0_2 = wave_utils.get_poly_line_by_point(wave.point_list[0], wave.point_list[2])
        
            target_points = self.all_points_df.loc[wave.point_list[0].time_offset:wave.point_list[3].time_offset]
            for point in target_points["point"]:
                diff1 = point.price - line0_2(point.time_offset)
                diff2 = point.price - line1_3(point.time_offset)
                if abs(diff1) < 0.01 or abs(diff2) < 0.01:
                    continue
                    
                if diff1 * diff2 > 0:
                    return False
            
            # 两条线应当不相交
            if (wave.point_list[1].price - line0_2(wave.point_list[1].time_offset)) * (wave.point_list[3].price - line0_2(wave.point_list[3].time_offset)) < 0:
                return False
            if (wave.point_list[0].price - line1_3(wave.point_list[0].time_offset)) * (wave.point_list[2].price - line1_3(wave.point_list[2].time_offset)) < 0:
                return False
            
        return True
    
    def get_next_point_limit(self, wave_type, point_list):
        limit_map = {}
        
        # 点在1-3、2-4 的连线内意味着，1-3、2-4 是相邻的凸包节点。
        # 即点3是点1为极坐标中心的下一个凸包节点。
        # 将对应范围内的点加入凸包进行计算，并检测其是否是凸包节点
        if issubclass(wave_type, waves.TriangleWave):         
            if len(point_list) < 3 or len(point_list) > 4:
                return limit_map    
            existing_points = self.all_points_df.loc[point_list[1].time_offset:point_list[-1].time_offset]
        elif issubclass(wave_type, waves.FlatWave):
            if len(point_list) < 2:
                return limit_map
            existing_points = self.all_points_df.loc[point_list[0].time_offset:point_list[-1].time_offset]
        else:
            return limit_map
        
        remaining_points = self.all_points_df.loc[point_list[-1].time_offset:]
        if len(remaining_points) <= 1:
            return limit_map
        remaining_points = remaining_points[1:]
        
        # 保证至少有3个点
        init_columns = (existing_points["time_offset"], existing_points["price"])
        hull_points = np.vstack(init_columns).T
        if len(hull_points) == 2:
            additional_point = remaining_points.iloc[0]
            hull_points = np.append(hull_points, [[additional_point.time_offset, additional_point.price]], axis=0)
        # 不断把 remaining_points 加入凸包，并判断当前点是否在凸包上
        hull = ConvexHull(hull_points, incremental=True)
        remaining_points_result = set()
        failed_for_remaining_points = False
        for point in remaining_points["point"]:
            hull.add_points([[point.time_offset, point.price]])
            hull_boundary_time_offset_list = [x[0] for x in hull.points[hull.vertices]]
            hull_boundary_time_offset = set(hull_boundary_time_offset_list)
            
            # 已经在浪上的点必须始终在凸包上
            for must_exist_point in point_list[1:]:
                if must_exist_point.time_offset not in hull_boundary_time_offset:
                    failed_for_remaining_points = True
                    break
            if failed_for_remaining_points:
                break
                
            # 点1-3, 2-4 应当是凸包上的相邻节点
            if len(existing_points) > 1:
                next_point = point_list[-2]
                next_point_index = hull_boundary_time_offset_list.index(next_point.time_offset)
                if hull_boundary_time_offset_list[(next_point_index+1) % len(hull_boundary_time_offset_list)] != point.time_offset and hull_boundary_time_offset_list[next_point_index-1] != point.time_offset:
                    continue

            if point.time_offset in hull_boundary_time_offset:
                remaining_points_result.add(point.time_offset)

        limit_map["limit_func"] = self.get_wave_barrier_limit_func(remaining_points_result)            
        return limit_map