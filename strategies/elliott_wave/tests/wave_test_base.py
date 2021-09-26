import unittest
class BaseWaveTest(unittest.TestCase):
    show_graph = True
    show_rule = True
    show_score_reason = True
        
    def assert_valid_wave(self, wave):
        if not wave.is_valid() and self.show_rule:
            for rule in wave.get_not_valid_rule():
                print(f"Wave is not valid because: {rule.desp}")
        self.assertTrue(wave.is_valid())
        
    def assert_wave_score(self, wave, target):
        wave_score = wave.get_score()
        if wave_score != target and self.show_score_reason:
            score_reason_dict = wave.get_score_contribution()
            for score_reason, score in score_reason_dict.items():
                print(score, score_reason)
        if wave_score != target and self.show_graph:
            wave.show_line_chart()
        self.assertEqual(wave_score, target)
        
    def assert_wave_match_rule(self, rule, wave):
        self.assertTrue(rule.validate(wave))
        
    def assert_wave_not_match_rule(self, rule, wave):
        self.assertFalse(rule.validate(wave))
        
    def assert_wave_match_guide(self, guide, wave, target):
        wave_score = guide.get_score(wave)
        if wave_score != target and self.show_score_reason:
            print(f"{guide.desp} not match {wave_score} != {target}")
        if wave_score != target and self.show_graph:
            wave.show_line_chart()
        self.assertEqual(wave_score, target)