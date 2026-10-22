import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from staff_matchup import batter_side, rank_candidates, support_inventory


class StaffTests(unittest.TestCase):
    def test_switch_hitters_change_sides_for_left_handed_pitchers(self):
        self.assertEqual(batter_side('S','R'),'L')
        self.assertEqual(batter_side('S','L'),'R')
        self.assertEqual(batter_side('L','L'),'L')

    def test_reference_mixes_and_rankings_are_separate_for_each_pitcher(self):
        frame=pd.DataFrame(dict(pitcher=['A','A','B','B'],batter=['X']*4,
            candidate_pitch=['FF','SL','SI','CH'],pitcher_count_pitch_support=[60,40,10,90],
            expected_batting_run_delta=[-.01,.02,.01,-.02]))
        ranked=rank_candidates(frame,['batter'])
        self.assertAlmostEqual(ranked[ranked.pitcher.eq('A')].usual_mix_batting_run_delta.iloc[0],.002)
        self.assertAlmostEqual(ranked[ranked.pitcher.eq('B')].usual_mix_batting_run_delta.iloc[0],-.017)
        self.assertEqual(ranked[ranked['rank'].eq(1)].candidate_pitch.tolist(),['FF','CH'])
        self.assertTrue(np.allclose((ranked.reference_mix_weight*ranked.erpa_runs_per_pitch).groupby(ranked.pitcher).sum(),0))

    def test_single_candidate_is_not_claimed_as_above_reference_improvement(self):
        frame=pd.DataFrame(dict(pitcher=['A'],batter=['X'],candidate_pitch=['FC'],
            pitcher_count_pitch_support=[0],expected_batting_run_delta=[.1]))
        result=rank_candidates(frame,['batter'])
        self.assertEqual(result.erpa_runs_per_pitch.iloc[0],0)
        self.assertEqual(result.reference_mix_weight.iloc[0],1)
        self.assertEqual(result['rank'].iloc[0],1)

    def test_repertoire_is_pitcher_specific_and_sparse_counts_are_flagged(self):
        def pitches(person,action):
            return pd.DataFrame(dict(pitcher=[person]*60,pitch_type=[action]*60,
                game_date=pd.to_datetime(['2026-09-01']*30+['2026-09-02']*30),stand=['L']*30+['R']*30,
                balls=[0]*60,strikes=[0]*60,previous_pitch_type=['START']*60,previous_result=['START']*60))
        data=pd.concat([pitches('1','SI'),pitches('2','FF')],ignore_index=True)
        batters=[dict(id=3,name='Switch',bat_side='S')]
        inventory,profile=support_inventory(data,dict(id=1,name='Lefty',throws='L'),batters)
        self.assertEqual(profile['repertoire'],['SI'])
        self.assertEqual(set(inventory.stand),{'R'})
        self.assertEqual(set(inventory.candidate_pitch),{'SI'})
        sparse=inventory[inventory.balls.eq(3)&inventory.strikes.eq(2)]
        self.assertTrue(sparse.support_fallback.all())
        self.assertTrue(sparse.pitcher_count_pitch_support.eq(0).all())
        # Reject an unsupported arsenal rather than silently using another pitcher's.
        with self.assertRaisesRegex(ValueError,'No supported repertoire'):
            support_inventory(data,dict(id=4,name='Missing',throws='L'),batters)


if __name__=='__main__':unittest.main()
