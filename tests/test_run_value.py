import sys
import unittest
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from run_value import add_base_outs, fit_run_weights, relative_value, run_values, COUNTS, reachable_states
from sequence import states_for
from matchup_model import LABELS


class RunValueTests(unittest.TestCase):
    def test_rare_previous_pitch_is_not_removed_by_next_action_rules(self):
        rows=[]
        for b,s,previous,result in states_for(['FF','CU']):
            for action in (['FF'] if (b,s)==(2,0) else ['FF','CU']):
                rows.append(dict(balls=b,strikes=s,previous_pitch=previous,previous_result=result,candidate_pitch=action))
        states=reachable_states(pd.DataFrame(rows))
        self.assertIn((3,0,'CU','ball'),states)
        self.assertNotIn((0,0,'CU','strike'),states)
        self.assertNotIn((2,1,'START','START'),states)

    def test_empty_string_runners_are_not_occupied_bases(self):
        data = pd.DataFrame({'outs_when_up': ['0', '2', '1'],
            'on_1b': ['', '123', None], 'on_2b': [np.nan, '', '456'], 'on_3b': ['', '789', '']})
        result = add_base_outs(data)
        self.assertEqual(result.base_mask.tolist(), [0, 5, 2])
        self.assertEqual(result.outs.tolist(), [0, 2, 1])

    def test_expectation_and_pitcher_sign(self):
        value = run_values([[.6, .4], [.2, .8]], [.1, -.1])
        np.testing.assert_allclose(value, [.02, -.06])
        baseline, saved = relative_value(value, [.5, .5])
        self.assertAlmostEqual(baseline, -.02)
        np.testing.assert_allclose(saved, [-.04, .04])
        self.assertAlmostEqual(saved @ np.array([.5, .5]), 0)
        with self.assertRaises(ValueError):
            run_values([[.5, .8]], [.1, -.1])

    def test_one_candidate_has_zero_above_mix_advantage(self):
        baseline, saved = relative_value([-.03], [5])
        self.assertAlmostEqual(baseline, -.03)
        self.assertAlmostEqual(saved[0], 0)

    def test_pooled_weights_cover_every_legal_situation_without_fake_support(self):
        frame = pd.DataFrame({'balls': [0] * len(LABELS), 'strikes': [0] * len(LABELS),
            'outs_when_up': [0] * len(LABELS), 'on_1b': [''] * len(LABELS),
            'on_2b': [''] * len(LABELS), 'on_3b': [''] * len(LABELS),
            'outcome': LABELS, 'delta_run_exp': np.linspace(-.3, .3, len(LABELS))})
        weights = fit_run_weights(frame)
        self.assertEqual(len(weights), 12 * 24 * len(LABELS))
        unseen = weights[(weights.balls==3) & (weights.strikes==2) & (weights.outs==2) & (weights.base_mask==7)]
        self.assertTrue(unseen.full_cell_n.eq(0).all())
        self.assertTrue(np.isfinite(unseen.expected_batting_run_delta).all())
        self.assertEqual(set(COUNTS), {(b,s) for b in range(4) for s in range(3)})


if __name__ == '__main__':
    unittest.main()
