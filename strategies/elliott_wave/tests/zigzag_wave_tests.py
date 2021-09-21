import unittest
import random
import wave_utils
import rules
import waves
import guides
from .wave_test_base import BaseWaveTest

class ZigZagWaveTests(BaseWaveTest):
    def test_rule22(self):
        wave = wave_utils.load_wave_from_dict({'type': 'ZigZagWave', 'points': [{'time_offset': 1, 'price': 103}, {'time_offset': 4, 'price': 102}, {'time_offset': 6, 'price': 107}, {'time_offset': 9, 'price': 100}], 'sub_wave': [None, None, None]})
        self.assert_wave_not_match_rule(rules.Rule22, wave)

        wave = wave_utils.load_wave_from_dict({'type': 'ZigZagWave', 'points': [{'time_offset': 8, 'price': 110}, {'time_offset': 9, 'price': 105}, {'time_offset': 11, 'price': 108}, {'time_offset': 12, 'price': 103}], 'sub_wave': [{'type': 'ImpluseWave', 'points': [], 'sub_wave': []}, {'type': 'ZigZagWave', 'points': [], 'sub_wave': []}, {'type': 'ImpluseWave', 'points': [], 'sub_wave': []}]})
        self.assert_wave_match_rule(rules.Rule22, wave)

    def test_guide_1_2_3_4_5_7_9(self):
        wave = wave_utils.load_wave_from_dict({'type': 'ZigZagWave', 'points': [{'time_offset': 8, 'price': 110}, {'time_offset': 9, 'price': 105}, {'time_offset': 11, 'price': 108}, {'time_offset': 12, 'price': 103}], 'sub_wave': [{'type': 'ImpluseWave', 'points': [], 'sub_wave': []}, {'type': 'ZigZagWave', 'points': [], 'sub_wave': []}, {'type': 'ImpluseWave', 'points': [], 'sub_wave': []}]})
        self.assert_wave_match_guide(guides.ZigZagWaveGuide1, wave, 1)
        self.assert_wave_match_guide(guides.ZigZagWaveGuide2, wave, 1)
        self.assert_wave_match_guide(guides.ZigZagWaveGuide3, wave, 1)
        self.assert_wave_match_guide(guides.ZigZagWaveGuide4, wave, 1)
        self.assert_wave_match_guide(guides.ZigZagWaveGuide5, wave, 1)
        self.assert_wave_match_guide(guides.ZigZagWaveGuide7, wave, 1)
        self.assert_wave_match_guide(guides.ZigZagWaveGuide9, wave, 1)
        
    def test_guide_8(self):
        wave = wave_utils.load_wave_from_dict({'type': 'ZigZagWave', 'points': [{'time_offset': 0, 'price': 102}, {'time_offset': 2, 'price': 104}, {'time_offset': 10, 'price': 103}, {'time_offset': 12, 'price': 105}], 'sub_wave': [{'type': 'ImpluseWave', 'points': [], 'sub_wave': []}, {'type': 'TriangleWave', 'points': [], 'sub_wave': []}, {'type': 'ImpluseWave', 'points': [], 'sub_wave': []}]})
        self.assert_wave_match_guide(guides.ZigZagWaveGuide8, wave, 1)
        
class ZigZagCombinationWaveTests(BaseWaveTest):
    def test_guide_1_2(self):
        wave = wave_utils.load_wave_from_dict({'type': 'ZigZagTripleCombinationWave', 'points': [{'time_offset': 2, 'price': 103}, {'time_offset': 6, 'price': 105}, {'time_offset': 8, 'price': 100}, {'time_offset': 12, 'price': 112}, {'time_offset': 14, 'price': 104}, {'time_offset': 18, 'price': 116}], 'sub_wave': [{'type': 'ZigZagWave', 'points': [], 'sub_wave': []}, {'type': 'TripleCombinationWave', 'points': [], 'sub_wave': []}, {'type': 'ZigZagWave', 'points': [], 'sub_wave': []}, {'type': 'TripleCombinationWave', 'points': [], 'sub_wave': []}, {'type': 'ZigZagWave', 'points': [], 'sub_wave': []}]})
        self.assert_wave_match_guide(guides.ZigzagCombinationWaveGuide1, wave, 1)
        self.assert_wave_match_guide(guides.ZigzagCombinationWaveGuide2, wave, 1)
        
class TripleCombinationWaveTests(BaseWaveTest):
    def test_guide_1_2(self):
        wave = wave_utils.load_wave_from_dict({'type': 'TripleCombinationWave', 'points': [{'time_offset': 1, 'price': 100}, {'time_offset': 3, 'price': 117}, {'time_offset': 5, 'price': 101}, {'time_offset': 8, 'price': 114}, {'time_offset': 11, 'price': 105}, {'time_offset': 19, 'price': 118}], 'sub_wave': [{'type': 'TripleCombinationWave', 'points': [], 'sub_wave': []}, {'type': 'TripleCombinationWave', 'points': [], 'sub_wave': []}, {'type': 'TripleCombinationWave', 'points': [], 'sub_wave': []}, {'type': 'TripleCombinationWave', 'points': [], 'sub_wave': []}, {'type': 'TripleCombinationWave', 'points': [], 'sub_wave': []}]})
        self.assert_wave_match_guide(guides.DoubleCombinationWaveGuide1, wave, 1)
        self.assert_wave_match_guide(guides.TripleCombinationWaveGuide1, wave, 1)