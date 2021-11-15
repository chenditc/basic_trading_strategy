from basic_types import *

class MotiveWave(Wave):
    """
    驱动浪
    """
    min_point_num = 6
    max_point_num = 6
    
class ImpluseWave(MotiveWave):
    """
    标准的推动5浪
    """
    is_concrete_wave = True
    def get_sub_wave_type_limit():
        """
        子浪类型的可选值列表
        """
        sub_wave_type_limit = [
            [ImpluseWave, LeadingDiagonalWave, ExtendImpluseWave],
            [CorrectiveWave],
            [ImpluseWave, ExtendImpluseWave],
            [ZigZagWave, FlatWave, TriangleWave, CombinationWave],
            [ImpluseWave, EndingDiagonalWave, ExtendImpluseWave],
        ]
        return sub_wave_type_limit

class ExtendImpluseWave(ImpluseWave):
    is_extend_wave = True
    
class DiagonalWave(MotiveWave):
    """
    斜纹浪
    """
    pass

class LeadingDiagonalWave(DiagonalWave):
    """
    引导斜纹浪
    """
    is_concrete_wave = True
    def get_sub_wave_type_limit():
        """
        子浪类型的可选值列表
        """
        sub_wave_type_limit = [
            [ZigZagWave, ImpluseWave],
            [ZigZagWave],
            [ZigZagWave, ImpluseWave],
            [ZigZagWave],
            [ZigZagWave, ImpluseWave],
        ]
        return sub_wave_type_limit

class EndingDiagonalWave(DiagonalWave):
    """
    终结斜纹浪
    """
    is_concrete_wave = True
    def get_sub_wave_type_limit():
        """
        子浪类型的可选值列表
        """
        sub_wave_type_limit = [
            [ZigZagWave],
            [ZigZagWave],
            [ZigZagWave],
            [ZigZagWave],
            [ZigZagWave],
        ]
        return sub_wave_type_limit
    
class CorrectiveWave(Wave):
    """
    调整浪
    """
    pass

class ZigZagWave(CorrectiveWave):
    """
    锯齿形调整浪
    """
    # 总是细分成3浪
    min_point_num = 4
    max_point_num = 4
    is_concrete_wave = True
    def get_sub_wave_type_limit():
        """
        子浪类型的可选值列表
        """
        sub_wave_type_limit = [
            [ImpluseWave, LeadingDiagonalWave],
            [CorrectiveWave],
            [ImpluseWave, EndingDiagonalWave],
        ]
        return sub_wave_type_limit

class FlatWave(CorrectiveWave):
    """
    平台型调整浪
    """
    # 总是细分成3浪
    min_point_num = 4
    max_point_num = 4
    is_concrete_wave = True
    def get_sub_wave_type_limit():
        """
        子浪类型的可选值列表
        """
        sub_wave_type_limit = [
            [ZigZagWave, FlatWave],
            [ZigZagWave, FlatWave, TriangleWave],
            [ImpluseWave, EndingDiagonalWave],
        ]
        return sub_wave_type_limit

class TriangleWave(CorrectiveWave):
    """
    三角形调整浪
    """
    min_point_num = 6
    max_point_num = 6
    def get_sub_wave_type_limit():
        """
        子浪类型的可选值列表
        """
        sub_wave_type_limit = [
            [ZigZagWave, ZigZagCombinationWave, TriangleWave],
            [ZigZagWave, ZigZagCombinationWave, TriangleWave],
            [ZigZagWave, ZigZagCombinationWave, TriangleWave],
            [ZigZagWave, ZigZagCombinationWave, TriangleWave],
            [ZigZagWave, ZigZagCombinationWave, TriangleWave]
        ]
        return sub_wave_type_limit
    
    def get_possible_subwave_combination(self):
        combinations = [[]]
        for wave_type_list in self.get_sub_wave_type_limit():
            new_combinations = []
            for wave_type in wave_type_list:
                for prev_comb in combinations:
                    # 至少4个是锯齿形调整浪，或锯齿形联合调整浪
                    if len([x for x in prev_comb if x != ZigZagWave and x != ZigZagCombinationWave]) > 0:
                        if wave_type != ZigZagWave and wave_type != ZigZagCombinationWave:
                            continue
                    # 不会有一个以上的复杂子浪，复杂子浪永远是锯齿形联合调整浪或者三角形调整浪
                    if len([x for x in prev_comb if x != ZigZagWave]) > 0:
                        if wave_type != ZigZagWave:
                            continue
                    new_combinations.append(prev_comb + [wave_type])
            combinations = new_combinations
        return combinations
    
class ContractingTriangleWave(TriangleWave):
    """
    收缩三角形调整浪
    """
    is_concrete_wave = True

class BarrierTriangleWave(TriangleWave):
    """
    屏障三角形调整浪
    """
    is_concrete_wave = True

class ExpandingTriangleWave(TriangleWave):
    """
    扩散三角形调整浪
    """
    is_concrete_wave = True

class CombinationWave(CorrectiveWave):
    """
    联合型调整浪
    """
    pass

class DoubleCombinationWave(CombinationWave):
    """
    双重三浪
    """
    min_point_num = 4
    max_point_num = 4
    is_concrete_wave = True
    def get_sub_wave_type_limit():
        """
        子浪类型的可选值列表
        """
        sub_wave_type_limit = [
            [ZigZagWave, FlatWave, CombinationWave],
            [CorrectiveWave],
            [ZigZagWave, FlatWave, CombinationWave],
        ]
        return sub_wave_type_limit

class TripleCombinationWave(CombinationWave):
    """
    三重三浪
    """
    min_point_num = 6
    max_point_num = 6
    is_concrete_wave = True
    def get_sub_wave_type_limit():
        """
        子浪类型的可选值列表
        """
        sub_wave_type_limit = [
            [ZigZagWave, FlatWave, CombinationWave],
            [ZigZagWave, FlatWave, CombinationWave],
            [ZigZagWave, FlatWave, CombinationWave],
            [CorrectiveWave],
            [ZigZagWave, FlatWave, CombinationWave],
        ]
        return sub_wave_type_limit

class ZigZagCombinationWave(CombinationWave):
    """
    锯齿形联合型调整浪
    """
    pass

class ZigZagDoubleCombinationWave(DoubleCombinationWave, ZigZagCombinationWave):
    """
    锯齿形双重联合型调整浪
    """
    is_concrete_wave = True
    def get_sub_wave_type_limit():
        """
        子浪类型的可选值列表
        """
        sub_wave_type_limit = [
            [ZigZagWave],
            [CorrectiveWave],
            [ZigZagWave],
        ]
        return sub_wave_type_limit

class ZigZagTripleCombinationWave(TripleCombinationWave, ZigZagCombinationWave):
    """
    锯齿形三重联合型调整浪
    """
    is_concrete_wave = True
    def get_sub_wave_type_limit():
        """
        子浪类型的可选值列表
        """
        sub_wave_type_limit = [
            [ZigZagWave],
            [CorrectiveWave],
            [ZigZagWave],
            [CorrectiveWave],
            [ZigZagWave],
        ]
        return sub_wave_type_limit
