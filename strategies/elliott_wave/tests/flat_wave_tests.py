import unittest
import random
import wave_utils
import rules
import waves
import guides
from .wave_test_base import BaseWaveTest

class FlatWaveTests(BaseWaveTest):
    def test_rule23(self):
        wave = wave_utils.load_wave_from_dict({'type': 'FlatWave', 'points': [{'time_offset': 1, 'price': 109}, {'time_offset': 3, 'price': 101}, {'time_offset': 7, 'price': 106}, {'time_offset': 9, 'price': 103}], 'sub_wave': [None, None, None]})
        self.assert_wave_not_match_rule(rules.Rule23, wave)

        wave = wave_utils.load_wave_from_dict({'type': 'FlatWave', 'points': [{'time_offset': 3, 'price': 104}, {'time_offset': 9, 'price': 107}, {'time_offset': 11, 'price': 103}, {'time_offset': 19, 'price': 110}], 'sub_wave': [{'type': 'ZigZagWave', 'points': [], 'sub_wave': []}, {'type': 'ZigZagWave', 'points': [], 'sub_wave': []}, {'type': 'ImpluseWave', 'points': [], 'sub_wave': []}]})
        self.assert_wave_match_rule(rules.Rule23, wave)

    def test_guide_1_2_3(self):
        wave = wave_utils.load_wave_from_dict({'type': 'FlatWave', 'points': [{'time_offset': 3, 'price': 104}, {'time_offset': 9, 'price': 107}, {'time_offset': 11, 'price': 103}, {'time_offset': 19, 'price': 110}], 'sub_wave': [{'type': 'ZigZagWave', 'points': [], 'sub_wave': []}, {'type': 'ZigZagWave', 'points': [], 'sub_wave': []}, {'type': 'ImpluseWave', 'points': [], 'sub_wave': []}]})
        self.assert_wave_match_guide(guides.FlatWaveGuide1, wave, 1)
        self.assert_wave_match_guide(guides.FlatWaveGuide2, wave, 1)
        self.assert_wave_match_guide(guides.FlatWaveGuide3, wave, 1)
        
    def test_expanded_flat_wave(self):
        wave = wave_utils.load_wave_from_dict({'type': 'FlatWave', 'points': [{'time_offset': 3, 'price': 104}, {'time_offset': 9, 'price': 107}, {'time_offset': 11, 'price': 103}, {'time_offset': 19, 'price': 110}], 'sub_wave': [{'type': 'ZigZagWave', 'points': [], 'sub_wave': []}, {'type': 'ZigZagWave', 'points': [], 'sub_wave': []}, {'type': 'ImpluseWave', 'points': [], 'sub_wave': []}]})
        self.assert_wave_match_guide(guides.ExpandedFlatWaveGuide, wave, 1)
        
    def test_regular_flat_wave(self):
        wave = wave_utils.load_wave_from_dict({'type': 'FlatWave', 'points': [{'time_offset': 4, 'price': 110}, {'time_offset': 6, 'price': 100}, {'time_offset': 9, 'price': 111}, {'time_offset': 12, 'price': 101}], 'sub_wave': [{'type': 'ZigZagWave', 'points': [], 'sub_wave': []}, {'type': 'ZigZagWave', 'points': [], 'sub_wave': []}, {'type': 'ImpluseWave', 'points': [], 'sub_wave': []}]})
        self.assert_wave_match_guide(guides.RegularFlatWaveGuide, wave, 1)
        
    def test_running_flat_wave(self):
        wave = wave_utils.load_wave_from_dict({'type': 'FlatWave', 'points': [{'time_offset': 5, 'price': 106}, {'time_offset': 12, 'price': 119}, {'time_offset': 14, 'price': 105}, {'time_offset': 18, 'price': 108}], 'sub_wave': [{'type': 'ZigZagWave', 'points': [], 'sub_wave': []}, {'type': 'ZigZagWave', 'points': [], 'sub_wave': []}, {'type': 'ImpluseWave', 'points': [], 'sub_wave': []}]})
        self.assert_wave_match_guide(guides.RunningFlatWaveGuide, wave, 1)
