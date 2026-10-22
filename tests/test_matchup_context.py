import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from improve_matchup import base_features, damage_priors, DAMAGE


class ContextTests(unittest.TestCase):
    def test_damage_excludes_current_day_and_future_and_keeps_pitch_profiles_separate(self):
        frame = pd.DataFrame(dict(
            pitcher=['A']*5, pitch_type=['FC','FC','FF','FC','FC'],
            game_date=pd.to_datetime(['2026-04-01','2026-04-01','2026-04-01','2026-04-02','2026-04-03']),
            description=['hit_into_play']*5, outcome=['single']*5,
            woba_value=[.9,.9,0,2,2], estimated_woba_using_speedangle=[.7,.5,.1,2,2],
            launch_speed=[100,96,70,115,115]))
        first=damage_priors(frame)
        self.assertEqual(first.loc[3,'prior_pitch_contacts'],2)
        self.assertAlmostEqual(first.loc[3,'prior_pitch_xwoba_contact'],(1.2+9.6)/32)
        changed=frame.copy()
        changed.loc[3:,['woba_value','estimated_woba_using_speedangle','launch_speed']]=0
        pd.testing.assert_frame_equal(first.loc[:3,DAMAGE],damage_priors(changed).loc[:3,DAMAGE])
        self.assertTrue(first.loc[:2,'prior_pitch_contacts'].eq(0).all())
        query=frame.iloc[[4,4]].copy()
        query['pitch_type']=['FC','FF'];query['outcome']=None
        query['description']=''
        result=damage_priors(pd.concat([frame.iloc[:3],query],ignore_index=True))
        self.assertEqual(result.loc[3,'prior_pitch_contacts'],2)
        self.assertEqual(result.loc[4,'prior_pitch_contacts'],1)

    def test_empty_string_runners_are_empty_and_runner_ids_are_not_features(self):
        frame=pd.DataFrame(dict(outs_when_up=[0,1,2],on_1b=['',123,np.nan],
            on_2b=[None,'',456],on_3b=[np.nan,789,999]))
        result=base_features(frame)
        self.assertEqual(result.base_mask.tolist(),[0,5,6])
        self.assertEqual(result.runner_1b.tolist(),[0,1,0])
        self.assertEqual(result.runner_2b.tolist(),[0,0,1])
        self.assertEqual(result.runner_3b.tolist(),[0,1,1])
        self.assertEqual(result.outs.tolist(),[0,1,2])
        frame.loc[1,'on_1b']=999999
        pd.testing.assert_frame_equal(result[['outs','runner_1b','runner_2b','runner_3b']],
            base_features(frame)[['outs','runner_1b','runner_2b','runner_3b']])


if __name__=='__main__':
    unittest.main()
