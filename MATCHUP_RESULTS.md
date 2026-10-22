# Matchup model improvements — October 21, 2026

The latest result is the [Misiorowski–Rays game plan](MIZ_RAYS_GAME_PLAN.md). It is a provisional decision aid for World Series Game 1, not a validated optimal strategy. The previous run-value regression remains unsupported; this new model predicts pitch transitions and uses an explicit approximate terminal-wOBA planner.

## Acquisition

All 30 player-season downloads (Miz plus 14 active Rays hitters, 2025 and 2026) reconcile exactly with MLB game-log physical pitch counts. Source files and checksums are recorded in the run manifest. The dataset has 44,981 unique usable pitches after overlap and automatic/unmapped events are removed. The cutoff is October 20. The original team dataset is unchanged.

## Two development rounds

| Feature round | Depth | Mean development log loss |
|---|---:|---:|
| Profiles + pre-pitch context | 2 | 1.638734 |
| Profiles + pre-pitch context | 3 | 1.638196 |
| Profiles + previous-pitch sequence | 2 | 1.638202 |
| Profiles + previous-pitch sequence | 3 | 1.637470 |

The sequence variant wins narrowly. Its incremental gain over the best profile/context variant is about 0.04%; this does not establish a large sequencing effect. All settings were selected with two chronological development folds before the new pitch-level test predictions were inspected. See [MATCHUP_PROTOCOL.md](MATCHUP_PROTOCOL.md).

## Locked postseason test

| Population | Pitches | Games | Model log loss | Context baseline | Global baseline |
|---|---:|---:|---:|---:|---:|
| overall | 1348 | 11 | 1.65625 | 1.68572 | 1.73655 |
| miz | 182 | 2 | 1.54285 | 1.56148 | 1.67411 |
| rays_hitters | 1166 | 9 | 1.67395 | 1.70511 | 1.74629 |

Overall improvement versus context is 1.75%. The 95% paired-game log-loss improvement interval is [0.01833, 0.04074]. The transition model passes its predictive acceptance gate. Miz's subset remains only two outings. Public aggregate postseason results were already known; the pitch-level predictions are newly held out.

## Forecast and planning

After locking the result, the selected architecture was refit on all available pregame observations. This forecast refit is not another test. The planner uses count, previous pitch and result, and candidate-specific prior physical and batter history. Alternative candidates get their own profiles; the actual chosen pitch’s measurements are never carried over to an alternative. Two-strike fouls loop, strike three ends the PA, and ball four walks.

Terminal weights are derived from observed woba_value: {'out': 0.0, 'single': 0.9000000000000002, 'extra_base': 1.2775531914893619, 'home_run': 2.0, 'hbp': 0.7000000000000001, 'walk': 0.6999999999999998}. The declared small pitch-usage cost is 0.0001 per pitch. The single category includes reached-on-error observations; weights and PA aggregation are approximate, not actual game run values.

Only Miz pitches with at least 50 2026 observations against the relevant handedness and five recent uses are eligible. Unsupported count options are removed where alternatives have support. Fastball, cutter, curveball, and slider qualify; rare changeup/sinker samples do not. Individual batter/right-handed-pitcher pitch-type counts are saved with each card.

**Most 0–0 action differences are very small.** The model’s fastball-first ranking is a lean, not evidence for throwing a predictable fastball to every hitter. The report includes close alternatives and count branches. Batters can adapt; intended location, catcher calls, warmup command, and fatigue are outside the causal model. Predictive loss improvement does not prove policy improvement.

## Reproduce and refresh

```bash
.venv/bin/python src/download_matchup.py
.venv/bin/python src/matchup_model.py
.venv/bin/python src/plan_matchup.py
```

The locked model command refuses to overwrite its run and reuse its final test for tuning. Downloading can resume checkpoints. Planning can be rerun to check the starter and upcoming batting order without changing the model. New data beyond the saved cutoff requires a declared new forecast refresh, not a relabeled test.

Source and model outputs are under `artifacts/miz_rays_20261023/`, including protocol, selection, manifest, model hashes, evaluation/forecast bundles, per-count policies, and forecast probabilities. The prepared frame is checksum-bound to the model report.

Lineup status at generation: provisional: latest completed-game order, not confirmed Game 1 lineup. The nine-player order shown is the last completed Rays game, not a confirmed Game 1 lineup. All 14 active batters have cards.
