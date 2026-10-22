import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from train_model import (FEATURES, TARGET, candidate_estimates, load_data,
                         make_features, normalize_columns, split_dates)
from history import add_history, HISTORY_NUMERIC
from model_policy import scoring_model


class TrainingSafetyTests(unittest.TestCase):
    def test_unproven_xgboost_does_not_replace_the_baseline(self):
        metrics = {"validation": {"training_mean": {"rmse": .3},
            "shrunk_context_mean": {"rmse": .4}, "xgboost": {"rmse": .2}},
            "test": {"training_mean": {"rmse": .3}, "shrunk_context_mean": {"rmse": .4},
                     "xgboost": {"rmse": .31}}}
        self.assertEqual(scoring_model(metrics, "xgboost", [-.01, .01], "rmse"), "training_mean")
        metrics["test"]["xgboost"]["rmse"] = .2
        self.assertEqual(scoring_model(metrics, "xgboost", [-.01, .1], "rmse"), "training_mean")
        self.assertEqual(scoring_model(metrics, "xgboost", [.01, .1], "rmse"), "xgboost")

    def test_history_excludes_current_date_and_all_future_outcomes(self):
        frame = pd.DataFrame({"game_date": pd.to_datetime(["2026-04-01", "2026-04-01", "2026-04-02", "2026-04-03"]),
            "pitcher": ["A"] * 4, "batter": ["B"] * 4,
            "delta_run_exp": [.1, .2, .3, .4], "description": ["ball"] * 4,
            "release_speed": [90, 92, 94, 96], "release_spin_rate": [2000] * 4,
            "release_extension": [6] * 4, "release_pos_x": [2] * 4, "release_pos_z": [5] * 4})
        result = add_history(frame)
        self.assertEqual(result.pitcher_prior_pitches.tolist(), [0, 0, 2, 3])
        self.assertAlmostEqual(result.loc[2, "pitcher_prior_release_speed"], 91)
        changed = frame.copy()
        changed.loc[2:, "delta_run_exp"] = 10
        changed.loc[2:, "release_speed"] = 150
        pd.testing.assert_series_equal(result.loc[2, HISTORY_NUMERIC], add_history(changed).loc[2, HISTORY_NUMERIC])

    def test_legacy_bom_header_is_recovered(self):
        frame = pd.DataFrame({'\ufeff"pitch_type"': ["FF"]})
        self.assertEqual(normalize_columns(frame)["pitch_type"].tolist(), ["FF"])

    def test_previous_pitch_requires_consecutive_same_plate_appearance(self):
        frame = pd.DataFrame({
            "game_pk": [1] * 5, "at_bat_number": [1, 1, 1, 1, 2],
            "pitch_number": [1, 2, 4, 5, 1], "pitcher": ["A", "A", "A", "B", "A"],
            "pitch_type": ["FF", "SL", "CH", "CU", "FF"],
            "description": ["ball", "called_strike", "foul", "ball", "ball"],
            "stand": ["R"] * 5, "p_throws": ["R"] * 5, "inning_topbot": ["Top"] * 5,
            "bat_score": [0] * 5, "fld_score": [0] * 5,
            "balls": [0] * 5, "strikes": [0] * 5, "outs_when_up": [0] * 5,
            "inning": [1] * 5, "on_1b": [np.nan] * 5,
            "on_2b": [np.nan] * 5, "on_3b": [np.nan] * 5,
        })
        features = make_features(frame)
        self.assertEqual(features.loc[1, "previous_pitch_type"], "FF")
        for i in [0, 2, 3, 4]:
            self.assertEqual(features.loc[i, "previous_pitch_type"], "NO_OBSERVED_PREVIOUS_PITCH")
        changed = frame.copy()
        changed.loc[1, "description"] = "home_run"
        self.assertEqual(make_features(changed).loc[1, "previous_description"], features.loc[1, "previous_description"])
        self.assertNotIn("description", FEATURES)
        self.assertNotIn(TARGET, FEATURES)

    def test_chronological_splits_keep_dates_and_games_together(self):
        data = pd.DataFrame({"game_date": np.repeat(pd.date_range("2026-04-01", periods=30), 100),
                             "game_pk": np.repeat(np.arange(30), 100)})
        train, validation, test = split_dates(data)
        self.assertLess(train.game_date.max(), validation.game_date.min())
        self.assertLess(validation.game_date.max(), test.game_date.min())
        self.assertFalse(set(train.game_pk) & set(test.game_pk))
        data.loc[data.index[-1], "game_pk"] = 0
        with self.assertRaisesRegex(ValueError, "game spans splits"):
            split_dates(data)

    def test_candidates_require_training_support(self):
        train = pd.DataFrame({"pitcher": ["A"] * 4, "stand": ["R"] * 4,
                              "pitch_type": ["FF", "FF", "SL", "CH"]})
        test = pd.DataFrame([{**dict.fromkeys(FEATURES, 0), "pitcher": "A", "stand": "R",
                              "pitch_type": "SL", "game_pk": 1, "at_bat_number": 1,
                              "game_date": pd.Timestamp("2026-09-01")}])

        class Encoder:
            def transform(self, x):
                return np.zeros((len(x), 1))

        class Model:
            def predict(self, x):
                return np.zeros(len(x))

        candidates = candidate_estimates(train, test, Encoder(), Model(), minimum=2)
        self.assertEqual(candidates.pitch_type.tolist(), ["FF"])
        self.assertEqual(candidates.training_support.tolist(), [2])

    def test_default_training_blocks_known_coverage_gaps(self):
        with tempfile.TemporaryDirectory() as temp:
            audit = Path(temp) / "audit.json"
            audit.write_text(json.dumps({"requested": {}, "pitchers": [{
                "name": "A", "player_id": "1", "regular_season_reconciliation": {
                    "missing_games": ["42"], "pitch_count_differences": []}}]}))
            with self.assertRaisesRegex(ValueError, "Known coverage gaps"):
                load_data(Path(temp), audit, False, "brewers")

    def test_loader_excludes_other_teams_and_discrepant_games(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            base = dict(game_date="2026-04-01", game_type="R", pitcher="1",
                pitch_type="FF", at_bat_number=1, pitch_number=1, stand="R",
                p_throws="R", inning_topbot="Top", description="ball",
                bat_score=0, fld_score=0, home_team="MIL", away_team="CHC",
                on_1b=np.nan, on_2b=np.nan, on_3b=np.nan, balls=0, strikes=0,
                outs_when_up=0, inning=1, delta_run_exp=.02)
            rows = [{**base, "game_pk": str(i)} for i in range(1, 5)]
            rows[1]["inning_topbot"] = "Bot"  # Opponent is pitching.
            rows[3][TARGET] = np.nan
            pd.DataFrame(rows).to_csv(root / "pitcher_1_2026.csv", index=False)
            audit = root / "audit.json"
            audit.write_text(json.dumps({"requested": {"season": 2026,
                "start": "2026-03-01", "end": "2026-09-21"}, "pitchers": [{
                    "name": "A", "player_id": "1", "regular_season_reconciliation": {
                        "missing_games": [], "pitch_count_differences": [{"game_pk": "3"}]}}]}))
            data, info = load_data(root, audit, True, "brewers")
            self.assertEqual(data.game_pk.tolist(), ["1"])
            self.assertEqual(info["excluded_discrepant_pitcher_game_rows"], 1)
            self.assertEqual(info["excluded_missing_target_or_pitch_type"], 1)
            rows[0]["pitcher"] = "2"
            pd.DataFrame(rows).to_csv(root / "pitcher_1_2026.csv", index=False)
            with self.assertRaisesRegex(ValueError, "another pitcher's data"):
                load_data(root, audit, True, "brewers")


if __name__ == "__main__":
    unittest.main()
