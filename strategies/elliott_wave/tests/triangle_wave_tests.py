import unittest
import random
import wave_utils
import rules
import waves
import guides
from .wave_test_base import BaseWaveTest

class TriangleWaveTests(BaseWaveTest):
    def test_rule25(self):
        wave = wave_utils.load_wave_from_dict({'type': 'TriangleWave', 'points': [{'time_offset': 1, 'price': 108}, {'time_offset': 2, 'price': 103}, {'time_offset': 4, 'price': 104}, {'time_offset': 7, 'price': 100}, {'time_offset': 8, 'price': 109}, {'time_offset': 9, 'price': 105}], 'sub_wave': [None, None, None, None, None]})
        self.assert_wave_not_match_rule(rules.Rule25, wave)

        wave = wave_utils.load_wave_from_dict({'type': 'TriangleWave', 'points': [{'time_offset': 2, 'price': 103}, {'time_offset': 6, 'price': 105}, {'time_offset': 8, 'price': 100}, {'time_offset': 12, 'price': 112}, {'time_offset': 14, 'price': 104}, {'time_offset': 18, 'price': 116}], 'sub_wave': [{'type': 'ZigZagWave', 'points': [], 'sub_wave': []}, {'type': 'ZigZagWave', 'points': [], 'sub_wave': []}, {'type': 'ZigZagCombinationWave', 'points': [], 'sub_wave': []}, {'type': 'ZigZagWave', 'points': [], 'sub_wave': []}, {'type': 'ZigZagWave', 'points': [], 'sub_wave': []}]})
        self.assert_wave_match_rule(rules.Rule25, wave)

    def test_rule26(self):
        wave = wave_utils.load_wave_from_dict({'type': 'TriangleWave', 'points': [{'time_offset': 0, 'price': 103}, {'time_offset': 1, 'price': 100}, {'time_offset': 5, 'price': 105}, {'time_offset': 6, 'price': 102}, {'time_offset': 7, 'price': 109}, {'time_offset': 8, 'price': 106}], 'sub_wave': [None, None, None, None, None]})
        self.assert_wave_not_match_rule(rules.Rule26, wave)

        wave = wave_utils.load_wave_from_dict({'type': 'TriangleWave', 'points': [{'time_offset': 2, 'price': 103}, {'time_offset': 6, 'price': 105}, {'time_offset': 8, 'price': 100}, {'time_offset': 12, 'price': 112}, {'time_offset': 14, 'price': 104}, {'time_offset': 18, 'price': 116}], 'sub_wave': [{'type': 'ZigZagWave', 'points': [], 'sub_wave': []}, {'type': 'ZigZagWave', 'points': [], 'sub_wave': []}, {'type': 'ZigZagCombinationWave', 'points': [], 'sub_wave': []}, {'type': 'ZigZagWave', 'points': [], 'sub_wave': []}, {'type': 'ZigZagWave', 'points': [], 'sub_wave': []}]})
        self.assert_wave_match_rule(rules.Rule26, wave)

    def test_rule27(self):
        wave = wave_utils.load_wave_from_dict({'type': 'ContractingTriangleWave', 'points': [{'time_offset': 0, 'price': 101}, {'time_offset': 1, 'price': 109}, {'time_offset': 3, 'price': 102}, {'time_offset': 4, 'price': 106}, {'time_offset': 5, 'price': 105}, {'time_offset': 7, 'price': 108}], 'sub_wave': [None, None, None, None, None]})
        self.assert_wave_not_match_rule(rules.Rule27, wave)

        wave = wave_utils.load_wave_from_dict({'type': 'ContractingTriangleWave', 'points': [{'time_offset': 0, 'price': 110}, {'time_offset': 1, 'price': 100}, {'time_offset': 6, 'price': 119}, {'time_offset': 8, 'price': 103}, {'time_offset': 12, 'price': 111}, {'time_offset': 13, 'price': 104}], 'sub_wave': [{'type': 'ZigZagWave', 'points': [], 'sub_wave': []}, {'type': 'ZigZagCombinationWave', 'points': [], 'sub_wave': []}, {'type': 'ZigZagWave', 'points': [], 'sub_wave': []}, {'type': 'ZigZagWave', 'points': [], 'sub_wave': []}, {'type': 'ZigZagWave', 'points': [], 'sub_wave': []}]})
        self.assert_wave_match_rule(rules.Rule27, wave)
        
    def test_rule28(self):
        wave = wave_utils.load_wave_from_dict({'type': 'BarrierTriangleWave', 'points': [{'time_offset': 0, 'price': 104}, {'time_offset': 2, 'price': 100}, {'time_offset': 3, 'price': 109}, {'time_offset': 4, 'price': 102}, {'time_offset': 5, 'price': 105}, {'time_offset': 7, 'price': 103}], 'sub_wave': [None, None, None, None, None]})
        self.assert_wave_not_match_rule(rules.Rule28, wave)

        wave = wave_utils.load_wave_from_dict({'type': 'BarrierTriangleWave', 'points': [{'time_offset': 10, 'price': 101}, {'time_offset': 12, 'price': 116}, {'time_offset': 14, 'price': 107}, {'time_offset': 15, 'price': 115}, {'time_offset': 17, 'price': 108}, {'time_offset': 18, 'price': 112}], 'sub_wave': [{'type': 'ZigZagCombinationWave', 'points': [], 'sub_wave': []}, {'type': 'ZigZagWave', 'points': [], 'sub_wave': []}, {'type': 'ZigZagWave', 'points': [], 'sub_wave': []}, {'type': 'ZigZagWave', 'points': [], 'sub_wave': []}, {'type': 'ZigZagWave', 'points': [], 'sub_wave': []}]})
        self.assert_wave_match_rule(rules.Rule28, wave)
        
    def test_rule29(self):
        wave = wave_utils.load_wave_from_dict({'type': 'ExpandingTriangleWave', 'points': [{'time_offset': 0, 'price': 105}, {'time_offset': 1, 'price': 103}, {'time_offset': 3, 'price': 106}, {'time_offset': 7, 'price': 102}, {'time_offset': 8, 'price': 108}, {'time_offset': 9, 'price': 104}], 'sub_wave': [None, None, None, None, None]})
        self.assert_wave_not_match_rule(rules.Rule29, wave)

        wave = wave_utils.load_wave_from_dict({'type': 'ExpandingTriangleWave', 'points': [{'time_offset': 10, 'price': 106}, {'time_offset': 12, 'price': 115}, {'time_offset': 13, 'price': 108}, {'time_offset': 15, 'price': 116}, {'time_offset': 16, 'price': 107}, {'time_offset': 19, 'price': 118}], 'sub_wave': [{'type': 'ZigZagWave', 'points': [], 'sub_wave': []}, {'type': 'ZigZagWave', 'points': [], 'sub_wave': []}, {'type': 'ZigZagWave', 'points': [], 'sub_wave': []}, {'type': 'ZigZagWave', 'points': [], 'sub_wave': []}, {'type': 'ZigZagCombinationWave', 'points': [], 'sub_wave': []}]})
        self.assert_wave_match_rule(rules.Rule29, wave)
        
    def test_rule30(self):
        wave = wave_utils.load_wave_from_dict({'type': 'ExpandingTriangleWave', 'points': [{'time_offset': 2, 'price': 104}, {'time_offset': 4, 'price': 102}, {'time_offset': 5, 'price': 105}, {'time_offset': 6, 'price': 101}, {'time_offset': 8, 'price': 109}, {'time_offset': 9, 'price': 100}], 'sub_wave': [None, None, None, None, None]})
        self.assert_wave_not_match_rule(rules.Rule30, wave)

        wave = wave_utils.load_wave_from_dict({'type': 'ExpandingTriangleWave', 'points': [{'time_offset': 10, 'price': 106}, {'time_offset': 12, 'price': 115}, {'time_offset': 13, 'price': 108}, {'time_offset': 15, 'price': 116}, {'time_offset': 16, 'price': 107}, {'time_offset': 19, 'price': 118}], 'sub_wave': [{'type': 'ZigZagWave', 'points': [], 'sub_wave': []}, {'type': 'ZigZagWave', 'points': [], 'sub_wave': []}, {'type': 'ZigZagWave', 'points': [], 'sub_wave': []}, {'type': 'ZigZagWave', 'points': [], 'sub_wave': []}, {'type': 'ZigZagCombinationWave', 'points': [], 'sub_wave': []}]})
        self.assert_wave_match_rule(rules.Rule30, wave)
