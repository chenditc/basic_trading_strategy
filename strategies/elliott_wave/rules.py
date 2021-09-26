from basic_types import *
import waves
import wave_utils

class PointNumberRule(Rule):
    desp = "不满足初始点个数要求"
    def validate(wave: Wave):
        if len(wave.point_list) < wave.min_point_num or len(wave.point_list) > wave.max_point_num:
            return False
        return True

class SubWaveRule():
    desp = ""
    @staticmethod
    def skip_empty_subwave_with_num(skip_sub_wave_num):
        def skip_empty_subwave(func):
            def validate_wrapper(wave: Wave):
                if len(wave.sub_wave) == 0:
                    return True
                # If not set, test all subwave
                if skip_sub_wave_num is None:
                    for this_sub_wave in wave.sub_wave:
                        if this_sub_wave is None:
                            return True
                else:
                    # If sub_wave_num is set, test only this subwave
                    if wave.sub_wave[skip_sub_wave_num] is None:
                        return True
                return func(wave)
            return validate_wrapper
        return skip_empty_subwave

class Rule0(Rule):
    desp = "浪的上升和下降应该间接出现"
    def validate(wave: Wave):
        point_left = wave.point_list[:-1]
        point_right = wave.point_list[1:]
        diff_list = [ x.price - y.price for x,y in zip(point_right, point_left)]
        sign_start = diff_list[0]
        for diff in diff_list[1:]:
            if sign_start * diff >= 0:
                return False
            sign_start = diff
        return True
    
class Rule1(SubWaveRule):
    desp = "浪1总是一个推动浪或者斜纹浪"    
    @SubWaveRule.skip_empty_subwave_with_num(0)
    def validate(wave: Wave):
        return isinstance(wave.sub_wave[0], waves.MotiveWave)

class Rule2(Rule):
    desp = "浪2永远不会超过浪1的起点"
    def validate(wave: Wave):
        move2 = wave.get_sub_wave_move_abs(1)
        move1 = wave.get_sub_wave_move_abs(0)
        return move2 < move1

class Rule3(SubWaveRule):
    desp = "浪2总是细分成一个锯齿形调整浪 Or 平台型调整浪 Or 联合型调整浪"
    @SubWaveRule.skip_empty_subwave_with_num(1)
    def validate(wave: Wave):
        return isinstance(wave.sub_wave[1], waves.ZigZagWave) or isinstance(wave.sub_wave[1], waves.FlatWave) or isinstance(wave.sub_wave[1], waves.CombinationWave) 

class Rule4(Rule):
    desp = "浪3永远不是最短的一浪"
    def validate(wave: Wave):
        wave_start_point = wave.point_list[:-1]
        wave_end_point = wave.point_list[1:]
        time_period_list = [ a.time_offset - b.time_offset for a, b in zip(wave_end_point, wave_start_point)]
        min_time = min(time_period_list)
        return time_period_list[2] > min_time
                
class Rule5(SubWaveRule):
    desp = "浪3总是一个推动浪"
    @SubWaveRule.skip_empty_subwave_with_num(2)
    def validate(wave: Wave):
        return isinstance(wave.sub_wave[2], waves.MotiveWave)

class Rule6(Rule):
    desp = "浪3总是运动过浪1的终点"
    def validate(wave: Wave):
        move3 = wave.get_sub_wave_move_abs(2)
        move2 = wave.get_sub_wave_move_abs(1)        
        return move3 > move2

class Rule7(Rule):
    desp = "浪4永远不会进入浪1的价格区域"
    def validate(wave: Wave):
        # TODO: test using real max / min price
        move4 = wave.get_sub_wave_move_abs(3)
        move3 = wave.get_sub_wave_move_abs(2)
        move2 = wave.get_sub_wave_move_abs(1)
        return move4 < (move3 - move2)
        
class Rule8(SubWaveRule):
    desp = "浪4总是细分成一个锯齿形调整浪 Or 平台型调整浪Or 三角形调整浪 Or 联合型调整浪"
    @SubWaveRule.skip_empty_subwave_with_num(3)
    def validate(wave: Wave):
        return isinstance(wave.sub_wave[3], waves.CorrectiveWave)

class Rule9(SubWaveRule):
    desp = "浪5总是一个推动浪或者斜纹浪"
    @SubWaveRule.skip_empty_subwave_with_num(4)
    def validate(wave: Wave):
        return isinstance(wave.sub_wave[4], waves.MotiveWave)
    
class Rule10(SubWaveRule):
    desp = "浪1、3、5最多只有两个延长浪，不会3个都延长"
    def validate(wave: Wave):
        extend_num = 0
        for wave_num in [0,2,4]:
            if (wave.sub_wave[wave_num] and wave.sub_wave[wave_num].is_extend_wave):
                extend_num += 1
        return extend_num < 3
    
class Rule11(Rule):
    desp = "浪4一定会进入浪1的价格区域"
    def validate(wave: Wave):
        # TODO: test using real max / min price
        move4 = wave.get_sub_wave_move_abs(3)
        move3 = wave.get_sub_wave_move_abs(2)
        move2 = wave.get_sub_wave_move_abs(1)
        return move4 > (move3 - move2)
    
class Rule12(Rule):
    desp = "浪4永远不会运动过浪2的终点"
    def validate(wave: Wave):
        # TODO: test using real max / min price
        move4 = wave.get_sub_wave_move_abs(3)
        move3 = wave.get_sub_wave_move_abs(2)
        return move4 < move3

class Rule13(Rule):
    desp = "浪4总在浪1的价格区域内结束"
    def validate(wave: Wave):
        move4 = wave.get_sub_wave_move_abs(3)
        move3 = wave.get_sub_wave_move_abs(2)
        move2 = wave.get_sub_wave_move_abs(1)
        move1 = wave.get_sub_wave_move_abs(0)
        return (move1 - move2 + move3 - move4 > 0) and (move4 > (move3 - move2))
    
class Rule14(Rule):
    desp = "浪3一定会超过浪1的终点"
    def validate(wave: Wave):
        move3 = wave.get_sub_wave_move_abs(2)
        move2 = wave.get_sub_wave_move_abs(1)
        return move3 > move2
    
class Rule15(Rule):
    desp = "连接浪2终点和浪4终点的直线，会与浪1或浪3的直线汇聚或发散，会聚点不应在浪1-4的时间范围内"
    def validate(wave: Wave):
        converge_time, converge_price = wave_utils.get_points_line_converge_point(wave.point_list[1],
                                                                   wave.point_list[3],
                                                                   wave.point_list[2],
                                                                   wave.point_list[4])
        if converge_time is None:
            # 平行
            return False
        if converge_time > wave.point_list[0].time_offset and converge_time < wave.point_list[3].time_offset:
            return False
        return True
        
class Rule16(Rule):
    desp = "连接浪2终点和浪4终点的直线，会与浪1或浪3的直线汇聚或发散，如果是收缩斜纹浪，浪5短于浪3短于浪1，浪4短于浪2"
    def validate(wave: Wave):
        converge_time, converge_price = wave_utils.get_points_line_converge_point(wave.point_list[1],
                                                                   wave.point_list[3],
                                                                   wave.point_list[2],
                                                                   wave.point_list[4])
        if converge_time is None:
            # 平行
            return True
        is_converge = converge_time > wave.point_list[4].time_offset
        if not is_converge:
            # 发散，不适用该 rule
            return True
        # 浪5短于浪3
        if wave.get_sub_wave_time(4) >= wave.get_sub_wave_time(2):
            return False
        # 浪3短于浪1
        if wave.get_sub_wave_time(2) >= wave.get_sub_wave_time(0):
            return False
        # 浪4短于浪2
        if wave.get_sub_wave_time(3) >= wave.get_sub_wave_time(1):
            return False
        return True
    
class Rule17(Rule):
    desp = "连接浪2终点和浪4终点的直线，会与浪1或浪3的直线汇聚或发散，如果是扩散斜纹浪，浪5长于浪3长于浪1，浪4长于浪2"
    def validate(wave: Wave):
        converge_time, converge_price = wave_utils.get_points_line_converge_point(wave.point_list[1],
                                                                   wave.point_list[3],
                                                                   wave.point_list[2],
                                                                   wave.point_list[4])
        if converge_time is None:
            # 平行
            return True
        is_converge = converge_time > wave.point_list[4].time_offset
        if is_converge:
            # 收缩，不适用该 rule
            return True
        # 浪5长于浪3
        if wave.get_sub_wave_time(4) <= wave.get_sub_wave_time(2):
            return False
        # 浪3长于浪1
        if wave.get_sub_wave_time(2) <= wave.get_sub_wave_time(0):
            return False
        # 浪4长于浪2
        if wave.get_sub_wave_time(3) <= wave.get_sub_wave_time(1):
            return False
        return True
    
class Rule18(Rule):
    desp = "连接浪2终点和浪4终点的直线，会与浪1或浪3的直线汇聚或发散，如果是扩散斜纹浪，浪5终点总是超越浪3终点"
    def validate(wave: Wave):
        converge_time, converge_price = wave_utils.get_points_line_converge_point(wave.point_list[1],
                                                                   wave.point_list[3],
                                                                   wave.point_list[2],
                                                                   wave.point_list[4])
        if converge_time is None:
            # 平行
            return True
        is_converge = converge_time > wave.point_list[4].time_offset
        if is_converge:
            # 收缩，不适用该 rule
            return True
        move5 = wave.get_sub_wave_move_abs(4)
        move4 = wave.get_sub_wave_move_abs(3)
        return move5 > move4
    
class Rule19(SubWaveRule):
    desp = "所有子浪都是锯齿形调整浪"
    def validate(wave: Wave):
        for sub_wave in wave.sub_wave:
            if sub_wave is None:
                continue
            if isinstance(sub_wave, waves.ZigZagWave):
                continue
            else:
                return False
        return True

class Rule20(SubWaveRule):
    desp = "浪2和浪4总是锯齿形调整浪"
    def validate(wave: Wave):
        for index, sub_wave in enumerate(wave.sub_wave):
            if sub_wave is None:
                continue
            if index not in [1,3]:
                continue
            if isinstance(sub_wave, waves.ZigZagWave):
                continue
            else:
                return False
        return True
    
class Rule21(Rule):
    desp = "浪5总是超越浪3终点"
    def validate(wave: Wave):
        if abs(wave.point_list[5].price - wave.point_list[2].price) > abs(wave.point_list[3].price - wave.point_list[2].price):
            return True
        return False
    
class Rule22(Rule):
    desp = "浪B不会运动过浪A的起点"
    def validate(wave: Wave):
        move2 = wave.get_sub_wave_move_abs(1)
        move1 = wave.get_sub_wave_move_abs(0)
        return move2 < move1
    
class Rule23(Rule):
    desp = "浪B总是至少回撤掉浪A的90%"
    def validate(wave: Wave):
        move2 = wave.get_sub_wave_move_abs(1)
        move1 = wave.get_sub_wave_move_abs(0)
        return move2 > move1 * 0.9
    
class Rule24(SubWaveRule):
    desp = "至少4个是锯齿形调整浪，或锯齿形联合调整浪"
    def validate(wave: Wave):
        zigzag_wave_num = 0
        for sub_wave in wave.sub_wave:
            if sub_wave is None:
                zigzag_wave_num += 1
            if isinstance(sub_wave, waves.ZigZagWave):
                zigzag_wave_num += 1
            if isinstance(sub_wave, waves.ZigZagCombinationWave):
                zigzag_wave_num += 1
        return zigzag_wave_num >= 4
    
class Rule25(Rule):
    desp = "A-B-C-D-E 五个浪重叠，即点 0,2,4 和 1,3,5 在某条线两侧"
    def validate(wave: Wave):
        if wave.first_sub_wave_trend:
            max_0_2_4 = max([p.price for p in wave.point_list[::2]])
            min_1_3_5 = min([p.price for p in wave.point_list[1::2]])
            if max_0_2_4 < min_1_3_5:
                return True
        else:
            min_0_2_4 = min([p.price for p in wave.point_list[::2]])
            max_1_3_5 = max([p.price for p in wave.point_list[1::2]])
            if max_1_3_5 < min_0_2_4:
                return True
        return False
    
class Rule26(Rule):
    desp = "浪E的终点前对前一个更大一级的波浪产生净回撤"
    def validate(wave:Wave):
        if wave.first_sub_wave_trend:
            return wave.point_list[-1].price > wave.point_list[0].price
        else:
            return wave.point_list[-1].price < wave.point_list[0].price
        
class Rule27(Rule):
    desp = "浪C不会超过浪A的终点，浪D不会超过浪B的终点，浪E不会超过浪C的终点"
    def validate(wave:Wave):
        move_a = wave.get_sub_wave_move_abs(0)
        move_b = wave.get_sub_wave_move_abs(1)
        move_c = wave.get_sub_wave_move_abs(2)
        move_d = wave.get_sub_wave_move_abs(3)
        move_e = wave.get_sub_wave_move_abs(4)
        return (move_c < move_b and move_d < move_c and move_e < move_d)

class Rule28(Rule):
    desp = "浪B与浪D在同一水平位置结束"
    def validate(wave:Wave):
        move_c = wave.get_sub_wave_move_abs(2)
        move_d = wave.get_sub_wave_move_abs(3)
        return abs(move_c - move_d) < 0.01
    
class Rule29(Rule):
    desp = "浪C超过浪A的终点，浪D超过浪B的终点，浪E超过浪C的终点"
    def validate(wave:Wave):
        move_a = wave.get_sub_wave_move_abs(0)
        move_b = wave.get_sub_wave_move_abs(1)
        move_c = wave.get_sub_wave_move_abs(2)
        move_d = wave.get_sub_wave_move_abs(3)
        move_e = wave.get_sub_wave_move_abs(4)
        return (move_c > move_b and move_d > move_c and move_e > move_d)

class Rule30(Rule):
    desp = "浪B、C、D 都至少回撤100%，最多回撤150%"
    def validate(wave:Wave):
        move_a = wave.get_sub_wave_move_abs(0)
        move_b = wave.get_sub_wave_move_abs(1)
        move_c = wave.get_sub_wave_move_abs(2)
        move_d = wave.get_sub_wave_move_abs(3)
        move_e = wave.get_sub_wave_move_abs(4)
        return (move_c < move_b*1.5 and move_d < move_c*1.5 and move_e < move_d*1.5)
    
class Rule31(SubWaveRule):
    desp = "最多只有一个复杂浪"
    def validate(wave: Wave):
        complex_wave_num = 0
        for sub_wave in wave.sub_wave:
            if sub_wave is None:
                continue
            if not isinstance(sub_wave, waves.ZigZagWave):
                complex_wave_num += 1
        return complex_wave_num <= 1

waves.Wave.rule_list = [PointNumberRule, Rule0]
waves.ImpluseWave.rule_list = [PointNumberRule, Rule0, Rule1, Rule2, Rule3, Rule4, Rule5, Rule6, Rule7, Rule8, Rule9]

waves.DiagonalWave.rule_list = [PointNumberRule, Rule0, Rule11, Rule2, Rule12, Rule13, Rule14, Rule15, Rule16, Rule17, Rule18]
waves.EndingDiagonalWave.rule_list = waves.DiagonalWave.rule_list + [Rule19]
waves.LeadingDiagonalWave.rule_list = waves.DiagonalWave.rule_list + [Rule20, Rule21]

waves.CorrectiveWave.rule_list = waves.CorrectiveWave.rule_list + [Rule26]
waves.ZigZagWave.rule_list = waves.CorrectiveWave.rule_list + [Rule22]
waves.FlatWave.rule_list = waves.CorrectiveWave.rule_list + [Rule23]
waves.TriangleWave.rule_list = waves.CorrectiveWave.rule_list + [Rule24, Rule25, Rule31]
waves.ContractingTriangleWave.rule_list = waves.TriangleWave.rule_list + [Rule27]
waves.BarrierTriangleWave.rule_list = waves.ContractingTriangleWave.rule_list + [Rule28]
waves.ExpandingTriangleWave.rule_list = waves.TriangleWave.rule_list + [Rule29, Rule30]