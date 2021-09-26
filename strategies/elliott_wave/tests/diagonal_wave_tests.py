import unittest
import random
import wave_utils
import rules
import waves
import guides
from .wave_test_base import BaseWaveTest

class DiagonalWaveTests(BaseWaveTest):
    def test_rule11(self):
        wave = wave_utils.load_wave_from_dict({'type': 'DiagonalWave', 'points': [{'time_offset': 1, 'price': 103}, {'time_offset': 2, 'price': 105}, {'time_offset': 4, 'price': 104}, {'time_offset': 7, 'price': 109}, {'time_offset': 8, 'price': 106}, {'time_offset': 9, 'price': 108}], 'sub_wave': [None, None, None, None, None]})
        self.assert_wave_not_match_rule(rules.Rule11, wave)

        wave = wave_utils.load_wave_from_dict({'type': 'DiagonalWave', 'points': [{'time_offset': 1, 'price': 103}, {'time_offset': 2, 'price': 105}, {'time_offset': 4, 'price': 104}, {'time_offset': 7, 'price': 109}, {'time_offset': 8, 'price': 104}, {'time_offset': 9, 'price': 108}], 'sub_wave': [None, None, None, None, None]})
        self.assert_wave_match_rule(rules.Rule11, wave)

    def test_rule12(self):
        wave = wave_utils.load_wave_from_dict({'type': 'DiagonalWave', 'points': [{'time_offset': 0, 'price': 107}, {'time_offset': 1, 'price': 101}, {'time_offset': 2, 'price': 105}, {'time_offset': 4, 'price': 104}, {'time_offset': 7, 'price': 108}, {'time_offset': 9, 'price': 103}], 'sub_wave': [None, None, None, None, None]})
        self.assert_wave_not_match_rule(rules.Rule12, wave)
        
        wave = wave_utils.load_wave_from_dict({'type': 'DiagonalWave', 'points': [{'time_offset': 0, 'price': 100}, {'time_offset': 4, 'price': 112}, {'time_offset': 6, 'price': 103}, {'time_offset': 9, 'price': 107}, {'time_offset': 12, 'price': 104}, {'time_offset': 15, 'price': 113}], 'sub_wave': []})
        self.assert_wave_match_rule(rules.Rule12, wave)
        
    def test_rule13(self):
        wave = wave_utils.load_wave_from_dict({'type': 'DiagonalWave', 'points': [{'time_offset': 0, 'price': 106}, {'time_offset': 1, 'price': 101}, {'time_offset': 2, 'price': 109}, {'time_offset': 3, 'price': 107}, {'time_offset': 4, 'price': 108}, {'time_offset': 9, 'price': 103}], 'sub_wave': [None, None, None, None, None]})
        self.assert_wave_not_match_rule(rules.Rule13, wave)
        
        wave = wave_utils.load_wave_from_dict({'type': 'DiagonalWave', 'points': [{'time_offset': 0, 'price': 100}, {'time_offset': 4, 'price': 112}, {'time_offset': 6, 'price': 103}, {'time_offset': 9, 'price': 107}, {'time_offset': 12, 'price': 104}, {'time_offset': 15, 'price': 113}], 'sub_wave': []})
        self.assert_wave_match_rule(rules.Rule13, wave)

    def test_rule14(self):
        wave = wave_utils.load_wave_from_dict({'type': 'DiagonalWave', 'points': [{'time_offset': 2, 'price': 108}, {'time_offset': 3, 'price': 101}, {'time_offset': 5, 'price': 105}, {'time_offset': 6, 'price': 102}, {'time_offset': 7, 'price': 104}, {'time_offset': 9, 'price': 103}], 'sub_wave': [None, None, None, None, None]})
        self.assert_wave_not_match_rule(rules.Rule14, wave)
        
        wave = wave_utils.load_wave_from_dict({'type': 'DiagonalWave', 'points': [{'time_offset': 1, 'price': 116}, {'time_offset': 2, 'price': 103}, {'time_offset': 4, 'price': 114}, {'time_offset': 5, 'price': 101}, {'time_offset': 10, 'price': 113}, {'time_offset': 13, 'price': 107}], 'sub_wave': []})
        self.assert_wave_match_rule(rules.Rule14, wave)
        
    def test_rule15(self):
        wave = wave_utils.load_wave_from_dict({'type': 'DiagonalWave', 'points': [{'time_offset': 1, 'price': 100}, {'time_offset': 3, 'price': 103}, {'time_offset': 4, 'price': 101}, {'time_offset': 5, 'price': 109}, {'time_offset': 7, 'price': 102}, {'time_offset': 8, 'price': 104}], 'sub_wave': [None, None, None, None, None]})
        self.assert_wave_not_match_rule(rules.Rule15, wave)
        
        wave = wave_utils.load_wave_from_dict({'type': 'DiagonalWave', 'points': [{'time_offset': 6, 'price': 144}, {'time_offset': 8, 'price': 127}, {'time_offset': 14, 'price': 135}, {'time_offset': 23, 'price': 121}, {'time_offset': 32, 'price': 128}, {'time_offset': 45, 'price': 125}], 'sub_wave': []})
        self.assert_wave_match_rule(rules.Rule15, wave)
        
    def test_rule16(self):
        wave = wave_utils.load_wave_from_dict({'type': 'DiagonalWave', 'points': [{'time_offset': 0, 'price': 109}, {'time_offset': 2, 'price': 102}, {'time_offset': 4, 'price': 107}, {'time_offset': 5, 'price': 101}, {'time_offset': 6, 'price': 104}, {'time_offset': 9, 'price': 103}], 'sub_wave': [None, None, None, None, None]})
        self.assert_wave_not_match_rule(rules.Rule16, wave)
        
        wave = wave_utils.load_wave_from_dict({'type': 'DiagonalWave', 'points': [{'time_offset': 5, 'price': 149}, {'time_offset': 23, 'price': 126}, {'time_offset': 32, 'price': 145}, {'time_offset': 39, 'price': 116}, {'time_offset': 41, 'price': 130}, {'time_offset': 45, 'price': 101}], 'sub_wave': []})
        self.assert_wave_match_rule(rules.Rule16, wave)

    def test_rule17(self):
        wave = wave_utils.load_wave_from_dict({'type': 'DiagonalWave', 'points': [{'time_offset': 1, 'price': 100}, {'time_offset': 2, 'price': 106}, {'time_offset': 3, 'price': 102}, {'time_offset': 6, 'price': 107}, {'time_offset': 8, 'price': 103}, {'time_offset': 9, 'price': 108}], 'sub_wave': [None, None, None, None, None]})
        self.assert_wave_not_match_rule(rules.Rule17, wave)
        
        wave = wave_utils.load_wave_from_dict({'type': 'DiagonalWave', 'points': [{'time_offset': 5, 'price': 149}, {'time_offset': 23, 'price': 126}, {'time_offset': 32, 'price': 145}, {'time_offset': 39, 'price': 116}, {'time_offset': 41, 'price': 130}, {'time_offset': 45, 'price': 101}], 'sub_wave': []})
        self.assert_wave_match_rule(rules.Rule17, wave)
        
    def test_rule18(self):
        wave = wave_utils.load_wave_from_dict({'type': 'DiagonalWave', 'points': [{'time_offset': 1, 'price': 109}, {'time_offset': 3, 'price': 106}, {'time_offset': 6, 'price': 108}, {'time_offset': 7, 'price': 103}, {'time_offset': 8, 'price': 107}, {'time_offset': 9, 'price': 105}], 'sub_wave': [None, None, None, None, None]})
        self.assert_wave_not_match_rule(rules.Rule18, wave)
        
        wave = wave_utils.load_wave_from_dict({'type': 'DiagonalWave', 'points': [{'time_offset': 5, 'price': 149}, {'time_offset': 23, 'price': 126}, {'time_offset': 32, 'price': 145}, {'time_offset': 39, 'price': 116}, {'time_offset': 41, 'price': 130}, {'time_offset': 45, 'price': 101}], 'sub_wave': []})
        self.assert_wave_match_rule(rules.Rule18, wave)
        
    def test_guide3(self):
        wave = wave_utils.load_wave_from_dict({'type': 'DiagonalWave', 'points': [{'time_offset': 8, 'price': 109}, {'time_offset': 11, 'price': 104}, {'time_offset': 14, 'price': 108}, {'time_offset': 16, 'price': 102}, {'time_offset': 17, 'price': 106}, {'time_offset': 18, 'price': 101}], 'sub_wave': [None, None, {'type': 'ExtendImpluseWave', 'points': [], 'sub_wave': []}, None, None]})
        self.assert_wave_match_guide(guides.DiagonalWaveGuide3, wave, 2)
        
        wave = wave_utils.load_wave_from_dict({'type': 'DiagonalWave', 'points': [{'time_offset': 0, 'price': 101}, {'time_offset': 1, 'price': 109}, {'time_offset': 2, 'price': 106}, {'time_offset': 5, 'price': 110}, {'time_offset': 13, 'price': 108}, {'time_offset': 19, 'price': 115}], 'sub_wave': [None, None, {'type': 'ExtendImpluseWave', 'points': [], 'sub_wave': []}, None, None]})
        self.assert_wave_match_guide(guides.DiagonalWaveGuide3, wave, 0)
        
    def test_guide4(self):
        wave =wave_utils.load_wave_from_dict({'type': 'DiagonalWave', 'points': [{'time_offset': 1, 'price': 106}, {'time_offset': 6, 'price': 110}, {'time_offset': 9, 'price': 108}, {'time_offset': 11, 'price': 111}, {'time_offset': 12, 'price': 109}, {'time_offset': 13, 'price': 114}], 'sub_wave': [None, None, {'type': 'ExtendImpluseWave', 'points': [], 'sub_wave': []}, None, None]})

        self.assert_wave_match_guide(guides.DiagonalWaveGuide4, wave, 1)
        
        wave = wave_utils.load_wave_from_dict({'type': 'DiagonalWave', 'points': [{'time_offset': 0, 'price': 113}, {'time_offset': 6, 'price': 104}, {'time_offset': 11, 'price': 112}, {'time_offset': 16, 'price': 101}, {'time_offset': 17, 'price': 108}, {'time_offset': 18, 'price': 106}], 'sub_wave': [None, None, {'type': 'ExtendImpluseWave', 'points': [], 'sub_wave': []}, None, None]})

        self.assert_wave_match_guide(guides.DiagonalWaveGuide4, wave, 0)

    def test_guide5(self):
        wave = wave_utils.load_wave_from_dict({'type': 'DiagonalWave', 'points': [{'time_offset': 1, 'price': 116}, {'time_offset': 6, 'price': 103}, {'time_offset': 9, 'price': 113}, {'time_offset': 11, 'price': 102}, {'time_offset': 13, 'price': 110}, {'time_offset': 14, 'price': 100}], 'sub_wave': [None, None, {'type': 'ExtendImpluseWave', 'points': [], 'sub_wave': []}, None, None]})
        self.assert_wave_match_guide(guides.DiagonalWaveGuide5, wave, 1)

    def test_guide6(self):
        wave = wave_utils.load_wave_from_dict({'type': 'DiagonalWave', 'points': [{'time_offset': 1, 'price': 107}, {'time_offset': 2, 'price': 111}, {'time_offset': 4, 'price': 108}, {'time_offset': 6, 'price': 113}, {'time_offset': 11, 'price': 110}, {'time_offset': 19, 'price': 116}], 'sub_wave': [None, None, {'type': 'ExtendImpluseWave', 'points': [], 'sub_wave': []}, None, None]})

        self.assert_wave_match_guide(guides.DiagonalWaveGuide6, wave, 1)

        
class EndingDiagonalWaveTests(BaseWaveTest):
    def test_rule19(self):
        wave = wave_utils.load_wave_from_dict({'type': 'DiagonalWave', 'points': [{'time_offset': 5, 'price': 149}, {'time_offset': 23, 'price': 126}, {'time_offset': 32, 'price': 145}, {'time_offset': 39, 'price': 116}, {'time_offset': 41, 'price': 130}, {'time_offset': 45, 'price': 101}], 'sub_wave': []})
        wave.sub_wave = [waves.ImpluseWave()]
        self.assert_wave_not_match_rule(rules.Rule19, wave)

        wave.sub_wave = [waves.ZigZagWave()]
        self.assert_wave_match_rule(rules.Rule19, wave)

class LeadingDiagonalWaveTests(BaseWaveTest):
    def test_rule20(self):
        wave = wave_utils.load_wave_from_dict({'type': 'DiagonalWave', 'points': [{'time_offset': 5, 'price': 149}, {'time_offset': 23, 'price': 126}, {'time_offset': 32, 'price': 145}, {'time_offset': 39, 'price': 116}, {'time_offset': 41, 'price': 130}, {'time_offset': 45, 'price': 101}], 'sub_wave': []})
        wave.sub_wave = [waves.ImpluseWave()] * 5
        self.assert_wave_not_match_rule(rules.Rule20, wave)

        wave.sub_wave[1] = waves.ZigZagWave()
        wave.sub_wave[3] = waves.ZigZagWave()
        self.assert_wave_match_rule(rules.Rule20, wave)
        
    def test_rule21(self):
        wave = wave_utils.load_wave_from_dict({'type': 'LeadingDiagonalWave', 'points': [{'time_offset': 0, 'price': 109}, {'time_offset': 2, 'price': 103}, {'time_offset': 3, 'price': 107}, {'time_offset': 5, 'price': 100}, {'time_offset': 6, 'price': 104}, {'time_offset': 7, 'price': 102}], 'sub_wave': [None, None, None, None, None]})
        self.assert_wave_not_match_rule(rules.Rule21, wave)

        wave = wave_utils.load_wave_from_dict({'type': 'LeadingDiagonalWave', 'points': [{'time_offset': 5, 'price': 149}, {'time_offset': 23, 'price': 126}, {'time_offset': 32, 'price': 145}, {'time_offset': 39, 'price': 116}, {'time_offset': 41, 'price': 130}, {'time_offset': 45, 'price': 101}], 'sub_wave': []})
        self.assert_wave_match_rule(rules.Rule21, wave)