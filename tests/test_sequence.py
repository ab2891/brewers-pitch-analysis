import sys
import unittest
from pathlib import Path
import numpy as np
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from sequence import continuation, solve, states_for
from matchup_model import with_priors


class SequenceTests(unittest.TestCase):
    def test_two_strike_foul_loop_has_the_correct_expected_pitch_cost(self):
        states = states_for(['FF'])
        probabilities = {(s, 'FF'): {'strike': .5, 'foul': .5} for s in states}
        _, scores = solve(states, ['FF'], probabilities, {'walk': .7})
        self.assertAlmostEqual(scores[(0, 2, 'FF', 'foul')]['FF'], .0002, places=7)
        self.assertAlmostEqual(scores[(0, 0, 'START', 'START')]['FF'], .0004, places=7)

    def test_count_rules_include_two_strike_foul_loop(self):
        self.assertEqual(continuation((1, 2, 'FF', 'strike'), 'CU', 'foul'), (1, 2, 'CU', 'foul'))
        self.assertIsNone(continuation((3, 1, 'FF', 'ball'), 'FF', 'ball'))
        self.assertIsNone(continuation((1, 2, 'FF', 'strike'), 'CU', 'whiff'))
        self.assertEqual(continuation((0, 0, 'START', 'START'), 'FF', 'strike'), (0, 1, 'FF', 'strike'))

    def test_planner_prefers_strikeouts_over_walks(self):
        actions = ['FF', 'CU']
        states = states_for(actions)
        probabilities = {(s, a): {'strike': 1.0} if a == 'FF' else {'ball': 1.0} for s in states for a in actions}
        policy, scores = solve(states, actions, probabilities, {'walk': .7})
        self.assertEqual(policy[(0, 0, 'START', 'START')], 'FF')
        self.assertAlmostEqual(scores[(0, 0, 'START', 'START')]['FF'], .0003)
        with self.assertRaisesRegex(ValueError, 'Invalid outcome'):
            solve(states, actions, {(s, a): {'strike': 2} for s in states for a in actions}, {'walk': .7})

    def test_pitch_profile_and_batter_history_exclude_same_day(self):
        frame = pd.DataFrame({'pitcher': ['1'] * 4, 'pitch_type': ['FF'] * 4,
            'batter': ['2'] * 4, 'stand': ['R'] * 4, 'p_throws': ['R'] * 4,
            'previous_pitch_type': ['START'] * 4, 'previous_result': ['START'] * 4,
            'game_date': pd.to_datetime(['2026-04-01', '2026-04-01', '2026-04-02', '2026-04-03']),
            'release_speed': [90, 94, 100, 100], 'release_spin_rate': [2000] * 4,
            'release_extension': [6] * 4, 'pfx_x': [1] * 4, 'pfx_z': [1] * 4,
            'outcome': ['ball', 'whiff', 'ball', 'ball'], 'woba_value': [np.nan] * 4})
        first = with_priors(frame)
        self.assertAlmostEqual(first.loc[2, 'prior_release_speed'], 92)
        self.assertEqual(first.loc[2, 'prior_pair_n'], 2)
        changed = frame.copy()
        changed.loc[2:, 'release_speed'] = 60
        changed.loc[2:, 'outcome'] = 'home_run'
        cols = ['prior_release_speed', 'prior_pair_n', 'prior_pair_whiff', 'prior_pair_ball']
        pd.testing.assert_series_equal(first.loc[2, cols], with_priors(changed).loc[2, cols])
        # A hypothetical curve must receive the curve's prior profile, not the
        # fastball profile from the observed action in the same decision context.
        frame.loc[1, 'pitch_type'] = 'CU'
        query = frame.iloc[[2, 2]].copy().reset_index(drop=True)
        query['pitch_type'] = ['FF', 'CU']
        query['outcome'] = None
        query['release_speed'] = np.nan
        result = with_priors(pd.concat([frame.iloc[:2], query], ignore_index=True))
        self.assertAlmostEqual(result.loc[2, 'prior_release_speed'], 90)
        self.assertAlmostEqual(result.loc[3, 'prior_release_speed'], 94)


if __name__ == '__main__':
    unittest.main()
