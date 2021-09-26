import unittest
import random
import wave_utils
from waves import *
from guides import *
from rules import *
from .wave_test_base import BaseWaveTest

class ImpluseWaveTests(BaseWaveTest):
    def test_PointNumberRule(self):
        wave = ImpluseWave([Point(0, 12)])
        self.assert_wave_not_match_rule(PointNumberRule, wave)
        
        wave = ImpluseWave([Point(0, 12),Point(1, 15),Point(3, 13),Point(5, 20),Point(8, 17),Point(9, 18),Point(9, 18)])
        self.assert_wave_not_match_rule(PointNumberRule, wave)
        
        wave = ImpluseWave([Point(0, 12),Point(1, 15),Point(3, 13),Point(5, 20),Point(8, 17),Point(9, 18)])
        self.assert_wave_match_rule(PointNumberRule, wave)
        
    def test_rule0(self):
        wave = ImpluseWave([Point(0, 12),Point(1, 15),Point(3, 13)])
        self.assert_wave_match_rule(Rule0, wave)
        
        wave = ImpluseWave([Point(0, 12),Point(1, 15),Point(3, 17)])
        self.assert_wave_not_match_rule(Rule0, wave)
        
    def test_rule1(self):
        wave = ImpluseWave([Point(0, 12),Point(1, 15),Point(3, 13),Point(5, 20),Point(8, 17),Point(9, 18)])
        wave.sub_wave[0] = ImpluseWave()
        self.assert_wave_match_rule(Rule1, wave)
        
        wave.sub_wave[0] = ZigZagWave()
        self.assert_wave_not_match_rule(Rule1, wave)
        
    def test_rule2(self):
        wave = ImpluseWave([Point(0, 12),Point(1, 15),Point(3, 13),Point(5, 20),Point(8, 17),Point(9, 18)])
        self.assert_wave_match_rule(Rule2, wave)
        
        wave = ImpluseWave([Point(0, 108),Point(1, 106),Point(4, 109),Point(6, 101),Point(7, 103),Point(9, 102)])
        self.assert_wave_not_match_rule(Rule2, wave)
        
    def test_rule3(self):
        wave = ImpluseWave([Point(0, 12),Point(1, 15),Point(3, 13),Point(5, 20),Point(8, 17),Point(9, 18)])
        wave.sub_wave[1] = ZigZagWave()
        self.assert_wave_match_rule(Rule3, wave)
        
        wave.sub_wave[1] = FlatWave()
        self.assert_wave_match_rule(Rule3, wave)
        
        wave.sub_wave[1] = CombinationWave()
        self.assert_wave_match_rule(Rule3, wave)
        
        wave.sub_wave[1] = ImpluseWave()
        self.assert_wave_not_match_rule(Rule3, wave)

        
    def test_rule4(self):
        wave = ImpluseWave([Point(0, 12),Point(1, 15),Point(3, 13),Point(5, 20),Point(8, 17),Point(9, 18)])
        self.assert_wave_match_rule(Rule4, wave)
        
        wave = ImpluseWave([Point(0, 109),Point(1, 105),Point(3, 108),Point(4, 100),Point(5, 104),Point(6, 101)])
        self.assert_wave_not_match_rule(Rule4, wave)

    def test_rule5(self):
        wave = ImpluseWave([Point(0, 12),Point(1, 15),Point(3, 13),Point(5, 20),Point(8, 17),Point(9, 18)])
        wave.sub_wave[2] = ZigZagWave()
        self.assert_wave_not_match_rule(Rule5, wave)
        
        wave.sub_wave[2] = FlatWave()
        self.assert_wave_not_match_rule(Rule5, wave)
        
        wave.sub_wave[2] = CombinationWave()
        self.assert_wave_not_match_rule(Rule5, wave)
        
        wave.sub_wave[2] = ImpluseWave()
        self.assert_wave_match_rule(Rule5, wave)
        
        wave.sub_wave[2] = DiagonalWave()
        self.assert_wave_match_rule(Rule5, wave)
        
    def test_rule6_7(self):
        wave = ImpluseWave([Point(0, 12),Point(1, 15),Point(3, 13),Point(5, 20),Point(8, 17),Point(9, 18)])
        self.assert_wave_match_rule(Rule6, wave)
        self.assert_wave_match_rule(Rule7, wave)
        
        wave = ImpluseWave([Point(0, 108),Point(1, 102),Point(2, 105),Point(4, 103),Point(5, 106),Point(8, 104)])
        self.assert_wave_not_match_rule(Rule6, wave)
        self.assert_wave_not_match_rule(Rule7, wave)

    def test_rule8(self):
        wave = ImpluseWave([Point(0, 12),Point(1, 15),Point(3, 13),Point(5, 20),Point(8, 17),Point(9, 18)])
        wave.sub_wave[3] = ZigZagWave()
        self.assert_wave_match_rule(Rule8, wave)
        
        wave.sub_wave[3] = FlatWave()
        self.assert_wave_match_rule(Rule8, wave)
        
        wave.sub_wave[3] = TriangleWave()
        self.assert_wave_match_rule(Rule8, wave)
        
        wave.sub_wave[3] = ZigZagCombinationWave()
        self.assert_wave_match_rule(Rule8, wave)
        
        wave.sub_wave[3] = ImpluseWave()
        self.assert_wave_not_match_rule(Rule8, wave)

    def test_rule9(self):
        wave = ImpluseWave([Point(0, 12),Point(1, 15),Point(3, 13),Point(5, 20),Point(8, 17),Point(9, 18)])
        wave.sub_wave[4] = ZigZagWave()
        self.assert_wave_not_match_rule(Rule9, wave)
        
        wave.sub_wave[4] = FlatWave()
        self.assert_wave_not_match_rule(Rule9, wave)
        
        wave.sub_wave[4] = CombinationWave()
        self.assert_wave_not_match_rule(Rule9, wave)
        
        wave.sub_wave[4] = ImpluseWave()
        self.assert_wave_match_rule(Rule9, wave)
        
        wave.sub_wave[4] = DiagonalWave()
        self.assert_wave_match_rule(Rule9, wave)
        
    def test_rule10(self):
        wave = ImpluseWave([Point(0, 12),Point(1, 15),Point(3, 13),Point(5, 20),Point(8, 17),Point(9, 18)])
        wave.sub_wave[0] = ImpluseWave()
        wave.sub_wave[2] = ImpluseWave()
        wave.sub_wave[4] = ImpluseWave()
        
        wave.sub_wave[4].is_extend_wave = True
        self.assert_wave_match_rule(Rule10, wave)
        
        wave.sub_wave[2].is_extend_wave = True
        self.assert_wave_match_rule(Rule10, wave)
        
        wave.sub_wave[0].is_extend_wave = True
        self.assert_wave_not_match_rule(Rule10, wave)

    def test_impluse_wave_guide_01(self):
        wave = ImpluseWave([Point(0, 19),Point(2, 17),Point(3, 18),Point(7, 10),Point(8, 16),Point(9, 11)])
        self.assert_valid_wave(wave)
        self.assert_wave_match_guide(ImpluseWaveGuide1, wave, 0)
        
        wave.sub_wave[2] = ImpluseWave()
        wave.sub_wave[2].is_extend_wave = True
        self.assert_wave_match_guide(ImpluseWaveGuide1, wave, 1)
        
    def test_impluse_wave_guide_02(self):
        wave = ImpluseWave([Point(0, 19),Point(2, 17),Point(3, 18),Point(7, 10),Point(8, 16),Point(9, 11)])
        self.assert_valid_wave(wave)
        self.assert_wave_match_guide(ImpluseWaveGuide2, wave, 0)
        
        wave.sub_wave[0] = ImpluseWave()
        wave.sub_wave[0].is_extend_wave = True
        self.assert_wave_match_guide(ImpluseWaveGuide2, wave, 0)
        
        wave.sub_wave[4] = ImpluseWave()
        wave.sub_wave[4].is_extend_wave = True
        self.assert_wave_match_guide(ImpluseWaveGuide2, wave, 0)
        
        wave.sub_wave[2] = ImpluseWave()
        wave.sub_wave[2].is_extend_wave = True
        self.assert_wave_match_guide(ImpluseWaveGuide2, wave, 1)
        
    def test_impluse_wave_guide_03(self):
        wave = ImpluseWave([Point(0, 19),Point(2, 17),Point(3, 18),Point(7, 10),Point(8, 16),Point(9, 11)])
        self.assert_valid_wave(wave)
        self.assert_wave_match_guide(ImpluseWaveGuide3, wave, 1)
        
        wave.sub_wave[0] = ImpluseWave()
        wave.sub_wave[0].is_extend_wave = True
        self.assert_wave_match_guide(ImpluseWaveGuide3, wave, 1)
        
        wave.sub_wave[4] = ImpluseWave()
        wave.sub_wave[4].is_extend_wave = True
        self.assert_wave_match_guide(ImpluseWaveGuide3, wave, 0)
        
    def test_impluse_wave_guide_04(self):
        wave = ImpluseWave([Point(0, 19),Point(2, 17),Point(3, 18),Point(7, 10),Point(8, 16),Point(9, 11)])
        self.assert_valid_wave(wave)
        self.assert_wave_match_guide(ImpluseWaveGuide4, wave, 1)
        
        wave.sub_wave[0] = ImpluseWave()
        wave.sub_wave[0].is_extend_wave = True
        self.assert_wave_match_guide(ImpluseWaveGuide4, wave, 0)

    def test_impluse_wave_guide_05(self):
        wave = ImpluseWave([Point(0, 19),Point(2, 17),Point(3, 18),Point(7, 10),Point(8, 16),Point(9, 11)])
        self.assert_valid_wave(wave)
        self.assert_wave_match_guide(ImpluseWaveGuide5, wave, 0)
        
        wave = wave_utils.load_wave_from_dict({'type': 'ImpluseWave', 'points': [{'time_offset': 1, 'price': 106}, {'time_offset': 7, 'price': 116}, {'time_offset': 19, 'price': 110}, {'time_offset': 23, 'price': 145}, {'time_offset': 28, 'price': 121}, {'time_offset': 31, 'price': 140}], 'sub_wave': [None, None, {'type': 'ExtendImpluseWave', 'points': [], 'sub_wave': []}, None, None]})
        wave.sub_wave[2] = ImpluseWave()
        wave.sub_wave[2].is_extend_wave = True
        self.assert_wave_match_guide(ImpluseWaveGuide5, wave, 1)
        
    def test_impluse_wave_guide_06(self):
        wave = ImpluseWave([Point(0, 19),Point(2, 17),Point(3, 18),Point(7, 10),Point(8, 16),Point(9, 11)])
        self.assert_valid_wave(wave)
        self.assert_wave_match_guide(ImpluseWaveGuide6, wave, 0)
        
        wave = ImpluseWave([Point(0, 102),Point(1, 106),Point(5, 103),Point(8, 118),Point(12, 109),Point(15, 116)])
        wave.sub_wave[4] = ImpluseWave()
        wave.sub_wave[4].is_extend_wave = True
        self.assert_wave_match_guide(ImpluseWaveGuide6, wave, 1)

    def test_impluse_wave_guide_07(self):
        wave = ImpluseWave([Point(0, 19),Point(2, 17),Point(3, 18),Point(7, 10),Point(8, 16),Point(9, 11)])
        self.assert_valid_wave(wave)
        self.assert_wave_match_guide(ImpluseWaveGuide7, wave, 0)
        
        wave.sub_wave[0] = DiagonalWave()
        wave.sub_wave[2] = ImpluseWave()
        wave.sub_wave[2].is_extend_wave = True
        self.assert_wave_match_guide(ImpluseWaveGuide7, wave, 1)
        
    def test_impluse_wave_guide_08(self):
        wave = ImpluseWave([Point(0, 19),Point(2, 17),Point(3, 18),Point(7, 10),Point(8, 16),Point(9, 11)])
        self.assert_valid_wave(wave)
        self.assert_wave_match_guide(ImpluseWaveGuide8, wave, 1)
        
        wave.sub_wave[2] = ImpluseWave()
        wave.sub_wave[2].is_extend_wave = True
        wave.sub_wave[4] = DiagonalWave()
        self.assert_wave_match_guide(ImpluseWaveGuide8, wave, 1)
        
        wave.sub_wave[2].is_extend_wave = False
        self.assert_wave_match_guide(ImpluseWaveGuide8, wave, 0)
        
    def test_impluse_wave_guide_09(self):
        wave = ImpluseWave([Point(0, 19),Point(2, 17),Point(3, 18),Point(7, 10),Point(8, 16),Point(9, 11)])
        self.assert_valid_wave(wave)
        self.assert_wave_match_guide(ImpluseWaveGuide9, wave, 0)
        
        wave.sub_wave[1] = ZigZagWave([Point(0, 17),Point(2, 18),Point(3, 17),Point(4, 18)])
        wave.sub_wave[3] = ZigZagWave([Point(0, 10),Point(2, 17),Point(3, 15),Point(4, 16)])
        self.assert_wave_match_guide(ImpluseWaveGuide9, wave, 1)
        
        
        wave.sub_wave[1] = ZigZagWave([Point(0, 17),Point(2, 19),Point(3, 18),Point(4, 18)])
        wave.sub_wave[3] = ZigZagWave([Point(0, 10),Point(2, 17),Point(3, 15),Point(4, 16)])
        self.assert_wave_match_guide(ImpluseWaveGuide9, wave, 0)
        
    def test_impluse_wave_guide_10(self):
        wave = ImpluseWave([Point(0, 19),Point(2, 17),Point(3, 18),Point(7, 10),Point(8, 16),Point(9, 11)])
        self.assert_valid_wave(wave)
        self.assert_wave_match_guide(ImpluseWaveGuide10, wave, 0)
        
        wave.sub_wave[1] = ZigZagCombinationWave()
        wave.sub_wave[3] = ZigZagWave()
        self.assert_wave_match_guide(ImpluseWaveGuide10, wave, 1)
        
        
        wave.sub_wave[1] = ZigZagWave()
        wave.sub_wave[3] = ZigZagWave()
        self.assert_wave_match_guide(ImpluseWaveGuide10, wave, 0)
        
        wave.sub_wave[1] = ZigZagCombinationWave()
        wave.sub_wave[3] = ZigZagCombinationWave()
        self.assert_wave_match_guide(ImpluseWaveGuide10, wave, 0)
        
    def test_impluse_wave_guide_11(self):
        wave = ImpluseWave([Point(0, 19),Point(2, 17),Point(3, 18),Point(7, 10),Point(8, 16),Point(9, 11)])
        self.assert_valid_wave(wave)
        self.assert_wave_match_guide(ImpluseWaveGuide11, wave, 0)
        
        wave.sub_wave[1] = FlatWave()
        self.assert_wave_match_guide(ImpluseWaveGuide11, wave, 0)
        
        wave.sub_wave[1] = ZigZagWave()
        self.assert_wave_match_guide(ImpluseWaveGuide11, wave, 1)
        
        wave.sub_wave[1] = ZigZagCombinationWave()
        self.assert_wave_match_guide(ImpluseWaveGuide11, wave, 1)
        
    def test_impluse_wave_guide_12(self):
        wave = ImpluseWave([Point(0, 19),Point(2, 17),Point(3, 18),Point(7, 10),Point(8, 16),Point(9, 11)])
        self.assert_valid_wave(wave)
        self.assert_wave_match_guide(ImpluseWaveGuide12, wave, 0)
        
        wave.sub_wave[3] = ZigZagWave()
        self.assert_wave_match_guide(ImpluseWaveGuide12, wave, 1)
        
        wave.sub_wave[3] = ZigZagCombinationWave()
        self.assert_wave_match_guide(ImpluseWaveGuide12, wave, 0)

        wave.sub_wave[3] = TriangleWave()
        self.assert_wave_match_guide(ImpluseWaveGuide12, wave, 1)
        
        wave.sub_wave[3] = DoubleCombinationWave()
        self.assert_wave_match_guide(ImpluseWaveGuide12, wave, 1)
        
    def test_impluse_wave_guide_13(self):
        wave = ImpluseWave([Point(0, 19),Point(2, 17),Point(3, 18),Point(7, 10),Point(8, 16),Point(9, 11)])
        self.assert_valid_wave(wave)
        self.assert_wave_match_guide(ImpluseWaveGuide13, wave, 1)
        
    def test_impluse_wave_guide_15(self):
        wave = ImpluseWave([Point(1, 10),Point(2, 14),Point(5, 12),Point(7, 18),Point(8, 15),Point(9, 20)])
        self.assert_valid_wave(wave)
        self.assert_wave_match_guide(ImpluseWaveGuide15, wave, 1)
        
    def test_impluse_wave_guide_16(self):
        wave = ImpluseWave([Point(0, 104),Point(9, 114),Point(10, 108),Point(16, 117),Point(17, 115),Point(19, 119)])
        self.assert_valid_wave(wave)
        self.assert_wave_match_guide(ImpluseWaveGuide16, wave, 1)
        
    def test_impluse_wave_guide_18(self):
        wave = ImpluseWave([Point(0, 11),Point(1, 14),Point(3, 13),Point(6, 20),Point(8, 16),Point(9, 20)])
        self.assert_valid_wave(wave)
        self.assert_wave_match_guide(ImpluseWaveGuide18, wave, 1)

    def test_impluse_wave_combination(self):
        self.assertEqual(len(wave_utils.get_possible_subwave_combination(ImpluseWave)), 972)

        