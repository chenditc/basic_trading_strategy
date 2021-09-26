import waves
import basic_types
import unittest
import wave_utils
import math

class WaveUtilsTest(unittest.TestCase):
    def test_get_wave_moving_ratio(self):
        wave = waves.ImpluseWave([basic_types.Point(0, 0), basic_types.Point(1, 3), basic_types.Point(2, 2), basic_types.Point(3, 6), basic_types.Point(4, 4), basic_types.Point(5, 7)])
        ratio_1_3 = wave_utils.get_wave_moving_ratio(wave.point_list[1], wave.point_list[3])
        ratio_2_4 = wave_utils.get_wave_moving_ratio(wave.point_list[2], wave.point_list[4])
        self.assertTrue(abs(ratio_1_3 - math.log(2)/2) < 0.0001)
        self.assertTrue(abs(ratio_2_4 - math.log(2)/2) < 0.0001)        
