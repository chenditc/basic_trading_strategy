from basic_types import *
from waves import *
import copy
import wave_utils

def wave_move_is_fibonacci(wave, wave_num_a, wave_num_b):
    """
    浪a 和 浪b 的净位移是斐波那契比率
    """
    move1 = wave.get_sub_wave_move_abs(wave_num_a)
    move2 = wave.get_sub_wave_move_abs(wave_num_b)
    if abs(move2/move1 - 0.618) < 0.01:
        return 1
    if abs(move1/move2 - 0.618) < 0.01:
        return 1
    return 0


class ImpluseWaveGuide1(Guide):
    desp = "其中一个驱动浪常常会延长，导致出现9浪"
    def get_score(wave:Wave):
        for i in range(5):
            if wave.sub_wave_is_extend(i):
                return 1
        return 0
    
class ImpluseWaveGuide2(Guide):
    desp = "浪3延长比较常见"
    def get_score(wave:Wave):
        if wave.sub_wave_is_extend(2):
            return 1
        return 0
    
class ImpluseWaveGuide3(Guide):
    desp = "两个浪都延长很罕见"
    def get_score(wave:Wave):
        extend_wave = 0
        for sub_wave_num in [0,2,4]:
            if wave.sub_wave_is_extend(sub_wave_num):
                extend_wave += 1
        if extend_wave == 2:
            return 0
        return 1

class ImpluseWaveGuide4(Guide):
    desp = "浪1最不可能延长"
    def get_score(wave:Wave):
        if wave.sub_wave_is_extend(0):
            return 0
        return 1

class ImpluseWaveGuide5(Guide):
    desp = "如果浪3延长，则浪1和浪5的净位移（上涨的幅度）往往相同或者是斐波那契比率"
    def get_score(wave:Wave):
        if not wave.sub_wave_is_extend(2):
            return 0
        return wave_move_is_fibonacci(wave, 0, 4)

class ImpluseWaveGuide6(Guide):
    desp = "浪5或者浪1延长时，它往往与另外两浪的净位移呈斐波那契关系"
    def get_score(wave:Wave):
        score = 0
        if wave.sub_wave_is_extend(0):
            score += wave_move_is_fibonacci(wave, 0, 4)
            score += wave_move_is_fibonacci(wave, 0, 2)
        if wave.sub_wave_is_extend(4):
            score += wave_move_is_fibonacci(wave, 0, 4)
            score += wave_move_is_fibonacci(wave, 2, 4)
        return score
    
class ImpluseWaveGuide7(Guide):
    desp = "如果浪1是斜纹浪，浪3很可能会延长"
    def get_score(wave:Wave):
        if wave.sub_wave[0] and isinstance(wave.sub_wave[0], DiagonalWave):
            if wave.sub_wave_is_extend(2):
                return 1
        return 0
    
class ImpluseWaveGuide8(Guide):
    desp = "如果浪3没有延长，浪5不太会是斜纹浪"
    def get_score(wave:Wave):
        # 三浪没有延长
        if not wave.sub_wave_is_extend(2):
            if wave.sub_wave[4] and isinstance(wave.sub_wave[4], DiagonalWave):
                return 0
        return 1

class ImpluseWaveGuide9(Guide):
    desp = "浪2和浪4的形态交替, 浪2和浪4的调整一个陡直：会包含前一个浪的终点，另一个横向，不包含"

    def get_score(wave:Wave):        
        def sub_wave_contains_start_point(wave, sub_wave_num=1):
            start_point = wave.point_list[sub_wave_num].price
            if not wave.sub_wave[sub_wave_num] or len(wave.sub_wave[sub_wave_num].point_list) == 0:
                return False
            price_list = [ x.price for x in wave.sub_wave[sub_wave_num].point_list[1:]]
            if min(price_list) <= start_point and start_point <= max(price_list):
                return True
            return False
        wave_2_contains_start_point = sub_wave_contains_start_point(wave, 1)
        wave_4_contains_start_point = sub_wave_contains_start_point(wave, 3)
        if wave_2_contains_start_point != wave_4_contains_start_point:
            return 1
        return 0

class ImpluseWaveGuide10(Guide):
    desp = "浪2和浪4的形态交替, 浪2和浪4的调整过程形态往往不同，一个简单，一个复杂"

    def get_score(wave:Wave):
        if isinstance(wave.sub_wave[1], CombinationWave) and not isinstance(wave.sub_wave[3], CombinationWave):
            return 1
        if isinstance(wave.sub_wave[3], CombinationWave) and not isinstance(wave.sub_wave[1], CombinationWave):
            return 1   
        return 0
    
class ImpluseWaveGuide11(Guide):
    desp = "浪2常是一个锯齿形调整浪 Or 锯齿形联合调整浪"
    def get_score(wave:Wave):
        if isinstance(wave.sub_wave[1], ZigZagWave):
            return 1
        # 锯齿形联合调整浪
        if isinstance(wave.sub_wave[1], ZigZagCombinationWave):
            return 1
        return 0
        
class ImpluseWaveGuide12(Guide):
    desp = "浪4总是一个锯齿形调整浪 Or 三角形调整浪 Or 平台型联合调整浪"
    def get_score(wave:Wave):
        if isinstance(wave.sub_wave[3], ZigZagWave):
            return 1
        if isinstance(wave.sub_wave[3], TriangleWave):
            return 1
        
        if isinstance(wave.sub_wave[3], CombinationWave) and not isinstance(wave.sub_wave[3], ZigZagCombinationWave):
            return 1
        return 0

class ImpluseWaveGuide13(Guide):
    desp = "当第五浪缩短时，第五浪未能超过第三浪，常出现在超强的第三浪后"
    def get_score(wave:Wave):
        if wave.get_sub_wave_move_abs(2) > wave.get_sub_wave_move_abs(0) * 2:
            # 第五浪未超过第三浪，即浪5的移动小于浪4
            if wave.get_sub_wave_move_abs(4) < wave.get_sub_wave_move_abs(3):
                return 1
        return 0
    
class ImpluseWaveGuide14(Guide):
    desp = "浪5预计较少的成交量"
    # TODO: implement me
    def get_score(wave:Wave):
        return 0

class ImpluseWaveGuide15(Guide):
    desp = "浪5常会以到达或者翻越过通道上沿结束"
    def get_score(wave:Wave):
        # 通过1-3上沿画一条线作为通道
        # TODO: 如果浪3太陡直，用浪2-4的斜率 + 浪1 的起点更合适
        ratio_1_3 = (wave.point_list[3].price - wave.point_list[1].price) / (wave.point_list[3].time_offset - wave.point_list[1].time_offset)
        ratio_1_5 = (wave.point_list[5].price - wave.point_list[1].price) / (wave.point_list[5].time_offset - wave.point_list[1].time_offset)
        # 翻越
        if abs(ratio_1_5) - abs(ratio_1_3) > 0 and (ratio_1_5 / ratio_1_3) < 1.1:
            return 1
        return 0

class ImpluseWaveGuide16(Guide):
    desp = "浪3的中心总有斜率最陡峭的部分，除了一部分浪1早期的可能会更陡峭"
    # TODO: implement me
    def get_score(wave:Wave):
        ratio1 = wave.get_sub_wave_move(0) / wave.get_sub_wave_time(0)
        ratio3 = wave.get_sub_wave_move(2) / wave.get_sub_wave_time(2)
        ratio5 = wave.get_sub_wave_move(4) / wave.get_sub_wave_time(4)
        
        score = 0
        if ratio3 > ratio1:
            score += 1
        if ratio3 > ratio5:
            score += 1
        if ratio1 > ratio3:
            score += 1
        return score

class ImpluseWaveGuide17(Guide):
    desp = "调整浪的深度，如果是第4浪，常在小一浪的第4浪的范围内结束。"
    # TODO: implement me
    def get_score(wave:Wave):
        return 0

class ImpluseWaveGuide18(Guide):
    desp = "浪4通常在时间或者价格上将整个推动浪划分为斐波那契比率"
    def get_score(wave:Wave):
        midpoint_price = (wave.point_list[5].price - wave.point_list[0].price) * 0.618 + wave.point_list[0].price
        midpoint_time = (wave.point_list[5].time_offset - wave.point_list[0].time_offset) * 0.618 + wave.point_list[0].time_offset
        # TODO: use max and min price instead
        if wave.point_list[4].price < midpoint_price and wave.point_list[3].price > midpoint_price:
            return 1
        if wave.point_list[3].time_offset < midpoint_time and midpoint_time < wave.point_list[4].time_offset:
            return 1
        return 0
    
class CorrectiveWaveGuide1(Guide):
    desp = "第五浪延长后，调整浪会是陡直的形态，会在延长浪的浪2位置结束或者支撑。"
    # TODO: implement me
    def get_score(wave:Wave):
        return 0

class DiagonalWaveGuide1(Guide):
    desp = "第五浪通常在“翻越”中结束，即最后一个子浪超过上边缘线"
    def get_score(wave:Wave):        
        target_price = wave_utils.get_line_extend_point(wave.point_list[1],
                                                        wave.point_list[3],
                                                        wave.point_list[5].time_offset)
        
        cross_length = abs(wave.point_list[5].price - wave.point_list[4].price) - abs(target_price - wave.point_list[4].price)
        if cross_length >= 0 and cross_length <= target_price * 0.1:
            return 1
        return 0
    
class DiagonalWaveGuide2(Guide):
    desp = "第五浪通常成交量极大"
    # TODO: implement me
    def get_score(wave:Wave):
        return 0
    
class DiagonalWaveGuide3(Guide):
    desp = "浪2和浪4通常回撤前一个波浪的0.66-0.81倍"
    def get_score(wave:Wave):
        move1 = wave.get_sub_wave_move_abs(0)
        move2 = wave.get_sub_wave_move_abs(1)
        move3 = wave.get_sub_wave_move_abs(2)
        move4 = wave.get_sub_wave_move_abs(3)
        
        score = 0
        if move2 / move1 >= 0.66 and move2/move1 < 0.81:
            score += 1
        if move4 / move3 >= 0.66 and move4/move3 < 0.81:
            score += 1
        return score
    
class DiagonalWaveGuide4(Guide):
    desp = "收缩斜纹浪中,浪5通常会超过浪3的终点"
    def get_score(wave:Wave):
        converge_time, converge_price = wave_utils.get_points_line_converge_point(wave.point_list[1],
                                                                   wave.point_list[3],
                                                                   wave.point_list[2],
                                                                   wave.point_list[4])
        if converge_time is None:
            # 平行
            return 0
        is_converge = converge_time > wave.point_list[4].time_offset
        if not is_converge:
            return 0
        
        if abs(wave.point_list[5].price - wave.point_list[2].price) > abs(wave.point_list[3].price - wave.point_list[2].price):
            return 1
        return 0
    
class DiagonalWaveGuide5(Guide):
    desp = "收缩斜纹浪中,浪5通常会在连接浪1、3终点的直线上或翻越结束"
    def get_score(wave:Wave):
        converge_time, converge_price = wave_utils.get_points_line_converge_point(wave.point_list[1],
                                                                   wave.point_list[3],
                                                                   wave.point_list[2],
                                                                   wave.point_list[4])
        if converge_time is None:
            # 平行
            return 0
        is_converge = converge_time > wave.point_list[4].time_offset
        if not is_converge:
            return 0
        
        target_price = wave_utils.get_line_extend_point(wave.point_list[1],
                                                        wave.point_list[3],
                                                        wave.point_list[5].time_offset)
        
        cross_length = abs(wave.point_list[5].price - wave.point_list[4].price) - abs(target_price - wave.point_list[4].price)
        if cross_length >= 0 and cross_length <= target_price * 0.1:
            return 1
        return 0
    
class DiagonalWaveGuide6(Guide):
    desp = "扩散斜纹浪中,浪5通常会略达不到浪1、3终点的直线结束"
    def get_score(wave:Wave):
        converge_time, converge_price = wave_utils.get_points_line_converge_point(wave.point_list[1],
                                                                   wave.point_list[3],
                                                                   wave.point_list[2],
                                                                   wave.point_list[4])
        if converge_time is None:
            # 平行
            return 0
        is_converge = converge_time > wave.point_list[4].time_offset
        if is_converge:
            return 0
        
        target_price = wave_utils.get_line_extend_point(wave.point_list[1],
                                                wave.point_list[3],
                                                wave.point_list[5].time_offset)
        
        cross_length = abs(wave.point_list[5].price - wave.point_list[4].price) - abs(target_price - wave.point_list[4].price)
        if cross_length < 0 and abs(cross_length) <= target_price * 0.1:
            return 1
        return 0

class ZigZagWaveGuide1(Guide):
    desp = "浪A常是推动浪"
    def get_score(wave:Wave):
        if wave.sub_wave[0] and isinstance(wave.sub_wave[0], ImpluseWave):
            return 1
        return 0
    
class ZigZagWaveGuide2(Guide):
    desp = "浪C常是推动浪"
    def get_score(wave:Wave):
        if wave.sub_wave[2] and isinstance(wave.sub_wave[2], ImpluseWave):
            return 1
        return 0
    
class ZigZagWaveGuide3(Guide):
    desp = "浪A、C长度相等"
    def get_score(wave:Wave):
        time1 = wave.get_sub_wave_time(0)
        time3 = wave.get_sub_wave_time(2)
        return abs(time1-time3)/time1 < 0.1

class ZigZagWaveGuide4(Guide):
    desp = "浪C的终点超过浪A的终点"
    def get_score(wave:Wave):
        move2 = wave.get_sub_wave_move_abs(1)
        move3 = wave.get_sub_wave_move_abs(2)
        return move3 > move2
    
class ZigZagWaveGuide5(Guide):
    desp = "浪B通常回撤掉浪A的38%-79%"
    def get_score(wave:Wave):
        move1 = wave.get_sub_wave_move_abs(0)
        move2 = wave.get_sub_wave_move_abs(1)
        if move2 > move1*0.38 and move2 < move1*0.79:
            return 1
        return 0
    
class ZigZagWaveGuide5(Guide):
    desp = "浪B通常回撤掉浪A的38%-79%"
    def get_score(wave:Wave):
        move1 = wave.get_sub_wave_move_abs(0)
        move2 = wave.get_sub_wave_move_abs(1)
        if move2 > move1*0.38 and move2 < move1*0.79:
            return 1
        return 0
    
class ZigZagWaveGuide6(Guide):
    desp = "如果C是一个顺势三角形调整浪，那么常回撤掉浪A的10-40%"
    def get_score(wave:Wave):
        # TODO: Implement me
        return 0
    
class ZigZagWaveGuide7(Guide):
    desp = "如果浪B是一个锯齿形调整浪，常回撤掉浪A的50%-79%"
    def get_score(wave:Wave):
        if not wave.sub_wave[1]:
            return 0
        if not isinstance(wave.sub_wave[1], ZigZagWave):
            return 0
        move1 = wave.get_sub_wave_move_abs(0)
        move2 = wave.get_sub_wave_move_abs(1)
        if move2 > move1*0.5 and move2 < move1*0.79:
            return 1
        return 0

class ZigZagWaveGuide8(Guide):
    desp = "如果浪B是一个三角形调整浪，常回撤掉浪A的38%-50%"
    def get_score(wave:Wave):
        if not wave.sub_wave[1]:
            return 0
        if not isinstance(wave.sub_wave[1], TriangleWave):
            return 0
        move1 = wave.get_sub_wave_move_abs(0)
        move2 = wave.get_sub_wave_move_abs(1)
        if move2 > move1*0.38 and move2 < move1*0.50:
            return 1
        return 0
    
class ZigZagWaveGuide9(Guide):
    desp = "浪C常在通道边界结束，通道是浪A起点与浪B终点连线平行经过浪A终点绘制的。"
    # 即 浪A起点与浪B终点的斜率与 浪C终点和浪A终点的斜率相近
    def get_score(wave:Wave):
        ratio1 = wave_utils.get_wave_moving_ratio(wave.point_list[0], wave.point_list[2])
        ratio2 = wave_utils.get_wave_moving_ratio(wave.point_list[1], wave.point_list[3])
        return abs(ratio1 - ratio2)/ratio2 < 0.1
    
class FlatWaveGuide1(Guide):
    desp = "浪B通常回撤掉浪A的100%-138%"
    def get_score(wave:Wave):
        move2 = wave.get_sub_wave_move_abs(1)
        move1 = wave.get_sub_wave_move_abs(0)
        if move2 > move1 and move2 < move1 * 1.38:
            return 1
        return 0
    
class FlatWaveGuide2(Guide):
    desp = "浪C的长度通常是浪A的100%-165%"
    def get_score(wave:Wave):
        time3 = wave.get_sub_wave_time(2)
        time1 = wave.get_sub_wave_time(0)
        if time3 > time1 and time3 < time1 * 1.65:
            return 1
        return 0
    
class FlatWaveGuide3(Guide):
    desp = "浪C的终点通常超过浪A的终点"
    def get_score(wave:Wave):
        move3 = wave.get_sub_wave_move_abs(2)
        move2 = wave.get_sub_wave_move_abs(1)
        if move3 > move2:
            return 1
        return 0
    
class RegularFlatWaveGuide(Guide):
    desp = "规则平台型，浪B在浪A起点附近结束，浪C在浪A终点附近结束"
    def get_score(wave:Wave):
        move3 = wave.get_sub_wave_move_abs(2)
        move2 = wave.get_sub_wave_move_abs(1)
        move1 = wave.get_sub_wave_move_abs(0)
        if wave_utils.value_close_to(move2, move1, 0.1) and wave_utils.value_close_to(move3, move2, 0.1):
            return 1
        return 0
    
class ExpandedFlatWaveGuide(Guide):
    desp = "扩散平台型，浪B超过浪A的起点位置，浪C远超过浪A终点位置结束"
    def get_score(wave:Wave):
        move3 = wave.get_sub_wave_move_abs(2)
        move2 = wave.get_sub_wave_move_abs(1)
        move1 = wave.get_sub_wave_move_abs(0)
        if move2 > move1 and move3 > move2 * 1.3:
            return 1
        return 0
    
class RunningFlatWaveGuide(Guide):
    desp = "顺势平台型，浪B超过浪A的起点位置，但是浪C达不到浪A的终点位置"
    def get_score(wave:Wave):
        move3 = wave.get_sub_wave_move_abs(2)
        move2 = wave.get_sub_wave_move_abs(1)
        move1 = wave.get_sub_wave_move_abs(0)
        if move2 > move1 and move3 < move2 * 0.9:
            return 1
        return 0

class TriangleWaveGuide1(Guide):
    desp = "通常浪C，偶尔浪D，会比其他子浪复杂"
    def get_score(wave:Wave):
        if not isinstance(wave.sub_wave[2], ZigZagWave):
            return 2
        if not isinstance(wave.sub_wave[3], ZigZagWave):
            return 1
        return 0
    
class TriangleWaveGuide2(Guide):
    desp = "通常复杂浪是多重锯齿形"
    def get_score(wave:Wave):
        for sub_wave in wave.sub_wave:
            if isinstance(sub_wave, ZigZagCombinationWave):
                return 1
        return 0
    
class TriangleWaveGuide3(Guide):
    desp = "常伴随成交量的减小"
    def get_score(wave:Wave):
        # TODO: implement me
        return 0
    
class TriangleWaveGuide4(Guide):
    desp = "复杂浪的回撤*百分比*比其他子浪大"
    def get_score(wave:Wave):
        move_a = wave.get_sub_wave_move_abs(0)
        move_b = wave.get_sub_wave_move_abs(1)
        move_c = wave.get_sub_wave_move_abs(2)
        move_d = wave.get_sub_wave_move_abs(3)
        move_e = wave.get_sub_wave_move_abs(4)
        
        max_move_ratio = -1
        max_move_wave_type = ZigZagWave
        for i in range(1,5):
            move_i = wave.get_sub_wave_move_abs(i)
            move_i_1 = wave.get_sub_wave_move_abs(i-1)
            move_ratio = move_i / move_i_1
            if move_ratio > max_move_ratio:
                max_move_ratio = move_ratio
                max_move_wave_type = wave.sub_wave[i]
        
        if max_move_wave_type is not None and max_move_wave_type != ZigZagWave:
            return 1
        return 0
    
class TriangleWaveGuide5(Guide):
    desp = "复杂浪的持续时间比其他子浪大"
    def get_score(wave:Wave):
        max_time = max([wave.get_sub_wave_time(i) for i in range(5)])
        for i in range(5):
            if not isinstance(wave.sub_wave[i], ZigZagWave) and max_time == wave.get_sub_wave_time(i):
                return 1
        return 0

class TriangleWaveGuide6(Guide):
    desp = "浪E 斜率比 BD 连线斜率大"
    def get_score(wave:Wave):
        ratio_e = wave_utils.get_wave_moving_ratio(wave.point_list[4], wave.point_list[5])
        ratio_b_d = wave_utils.get_wave_moving_ratio(wave.point_list[2], wave.point_list[4])
        return abs(ratio_e) > abs(ratio_b_d)
    
class ContractingTriangleWaveGuide1(Guide):
    desp = "浪E应该在AC、BD延长线交点的左侧"
    def get_score(wave:Wave):
        converge_time, converge_price = wave_utils.get_points_line_converge_point(wave.point_list[1],
                                                                   wave.point_list[3],
                                                                   wave.point_list[2],
                                                                   wave.point_list[4])
        if converge_time is None:
            # 平行
            return 0
        return converge_time > wave.point_list[5].time_offset

class ExpandingTriangleWaveGuide1(Guide):
    desp = "浪B、C、D 通常回撤105%～125%"
    def get_score(wave:Wave):
        score = 0
        move_b = wave.get_sub_wave_move_abs(1)
        move_c = wave.get_sub_wave_move_abs(2)
        move_d = wave.get_sub_wave_move_abs(3)
        move_e = wave.get_sub_wave_move_abs(4)
        
        score += (move_c > move_b * 1.05)
        score += (move_c < move_b * 1.25)
        score += (move_d > move_c * 1.05)
        score += (move_d < move_c * 1.25)
        score += (move_e > move_d * 1.05)
        score += (move_e < move_d * 1.25)
        return score
    
class ExpandingTriangleWaveGuide2(Guide):
    desp = "没有子浪是三角形调整浪"
    def get_score(wave:Wave):
        for sub_wave in wave.sub_wave:
            if isinstance(sub_wave, TriangleWave):
                return 0
        return 1
    
class ZigzagCombinationWaveGuide1(Guide):
    desp = "双重、三重锯齿形调整浪的第一个调整浪没有产生足够的价格调整，所以浪C的位移应该大于浪B，且多出来的部分与浪 A数量级接近"
    def get_score(wave:Wave):
        move_a = wave.get_sub_wave_move_abs(0)
        move_b = wave.get_sub_wave_move_abs(1)
        move_c = wave.get_sub_wave_move_abs(2)
        
        if move_c < move_b:
            return 0
        
        move_ratio = (move_c - move_b) / move_a
        if move_ratio > 0.2 and move_ratio < 5:
            return 1
        return 0
    
class ZigzagCombinationWaveGuide2(Guide):
    desp = "双重、三重锯齿形调整浪的第一个调整浪没有产生足够的价格调整，所以浪E的位移应该大于浪D，且多出来的部分与浪 A数量级接近"
    def get_score(wave:Wave):
        move_a = wave.get_sub_wave_move_abs(0)
        move_d = wave.get_sub_wave_move_abs(3)
        move_e = wave.get_sub_wave_move_abs(4)
        
        if move_e < move_d:
            return 0
        
        move_ratio = (move_e - move_d) / move_a
        if move_ratio > 0.2 and move_ratio < 5:
            return 1
        return 0
    
class DoubleCombinationWaveGuide1(Guide):
    desp = "双重、三重平台形调整浪的第一个调整浪已经产生足够的价格调整，所以浪C与浪B的位移差应该小于浪A的数量级"
    def get_score(wave:Wave):
        move_a = wave.get_sub_wave_move_abs(0)
        move_b = wave.get_sub_wave_move_abs(1)
        move_c = wave.get_sub_wave_move_abs(2)
        
        move_ratio = abs(move_c - move_b) / move_a
        if move_ratio < 0.2:
            return 1
        return 0
    
class TripleCombinationWaveGuide1(Guide):
    desp = "双重、三重平台形调整浪的第一个调整浪已经产生足够的价格调整，所以浪E终点应该距离浪A比较近"
    def get_score(wave:Wave):
        move_a = wave.get_sub_wave_move_abs(0)
        move_b = wave.get_sub_wave_move_abs(1)
        move_c = wave.get_sub_wave_move_abs(2)
        move_d = wave.get_sub_wave_move_abs(3)
        move_e = wave.get_sub_wave_move_abs(4)
        
        move_ratio = abs(move_e - move_d + move_c - move_b) / move_a
        if move_ratio < 0.2:
            return 1
        return 0
                
ImpluseWave.guide_dict = {
        ImpluseWaveGuide1: 1,
        ImpluseWaveGuide2: 1,
        ImpluseWaveGuide3: 1,
        ImpluseWaveGuide4: 1,
        ImpluseWaveGuide5: 1,
        ImpluseWaveGuide6: 1,
        ImpluseWaveGuide7: 1,
        ImpluseWaveGuide8: 1,
        ImpluseWaveGuide9: 1,
        ImpluseWaveGuide10: 1,
        ImpluseWaveGuide11: 1,
        ImpluseWaveGuide12: 1,
        ImpluseWaveGuide13: 1,
        ImpluseWaveGuide14: 1,
        ImpluseWaveGuide15: 1,
        ImpluseWaveGuide16: 1,
        ImpluseWaveGuide17: 1,
        ImpluseWaveGuide18: 1,
    }

DiagonalWave.guide_dict = {
    DiagonalWaveGuide3: 1,
    DiagonalWaveGuide4: 1,
    DiagonalWaveGuide5: 1,
    DiagonalWaveGuide6: 1
}

EndingDiagonalWave.guide_dict = copy.copy(DiagonalWave.guide_dict)
EndingDiagonalWave.guide_dict.update({
    DiagonalWaveGuide1: 1,
    DiagonalWaveGuide2: 1
})

LeadingDiagonalWave.guide_dict = copy.copy(DiagonalWave.guide_dict)

ZigZagWave.guide_dict = {
    ZigZagWaveGuide1: 1,
    ZigZagWaveGuide2: 1,
    ZigZagWaveGuide3: 1,
    ZigZagWaveGuide4: 1,
    ZigZagWaveGuide5: 1,
    ZigZagWaveGuide6: 1,
    ZigZagWaveGuide7: 1,
    ZigZagWaveGuide8: 1,
    ZigZagWaveGuide9: 1,
}

FlatWave.guide_dict = {
    FlatWaveGuide1 : 1,
    FlatWaveGuide2 : 1,
    FlatWaveGuide3 : 1,
    RegularFlatWaveGuide: 1,
    ExpandedFlatWaveGuide: 1,
    RunningFlatWaveGuide: 1
}

TriangleWave.guide_dict = {
    TriangleWaveGuide1: 1,
    TriangleWaveGuide2: 1,
    TriangleWaveGuide3: 1,
    TriangleWaveGuide4: 1,
    TriangleWaveGuide5: 1,
    TriangleWaveGuide6: 1,
}
ContractingTriangleWave.guide_dict = copy.copy(TriangleWave.guide_dict)
ContractingTriangleWave.guide_dict.update({
    ContractingTriangleWaveGuide1: 1
})

BarrierTriangleWave.guide_dict = copy.copy(TriangleWave.guide_dict)
ExpandingTriangleWave.guide_dict = copy.copy(TriangleWave.guide_dict)
ExpandingTriangleWave.guide_dict.update({
    ExpandingTriangleWaveGuide1: 1,
    ExpandingTriangleWaveGuide2: 1
})

ZigZagCombinationWave.guide_dict = {
    ZigzagCombinationWaveGuide1: 1
}

ZigZagTripleCombinationWave.guide_dict = {
    ZigzagCombinationWaveGuide1: 1,
    ZigzagCombinationWaveGuide2: 1
}

DoubleCombinationWave.guide_dict = {
    DoubleCombinationWaveGuide1: 1
}

TripleCombinationWave.guide_dict = {
    DoubleCombinationWaveGuide1: 1,
    TripleCombinationWaveGuide1: 1
}