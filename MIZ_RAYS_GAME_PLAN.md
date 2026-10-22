# Miz vs. Rays — provisional Game 1 pitch plan

For every count and runner/out context in run units, see the newer
[ERPA matchup report](ERPA_MATCHUP.md). This page retains the earlier approximate
terminal-wOBA sequence objective. The newer next-pitch run-value objective can
rank pitches differently.

**Friday, October 23, 2026 at 07:00 PM Central, American Family Field.**

Lineup status: provisional: latest completed-game order, not confirmed Game 1 lineup. The first nine rows use the latest completed Rays game's order, unless Game 1's order has been posted. Bench options follow. This is not an announced Game 1 batting order.

The table is a count-dependent model scenario, not a fixed script. Start with the opener; choose the next pitch from the observed ball/strike result. The 0–2 column follows two strikes on the displayed strike branch. A foul with two strikes keeps the count and triggers a new decision from the updated previous-pitch state.

| Batter | Side vs. Miz | Open 0–0 | If called strike, 0–1 | If ball, 1–0 | After two strikes, 0–2 | Opening alternative |
|---|---|---|---|---|---|---|
| Yandy Díaz | R | FF | FF | FC | FF | FC |
| Jonathan Aranda | L | FF | FF | FF | FF | FC |
| Liam Hicks | L | FF | FF | FC | FF | FC |
| Junior Caminero | R | FF | CU | FF | CU | CU |
| Chandler Simpson | L | FF | FF | FF | FF | FC |
| Victor Mesa Jr. | L | FF | FF | FF | FF | FC |
| Jonny DeLuca | R | FF | FF | FC | CU | FC |
| Richie Palacios | L | FF | SL | FC | SL | FC |
| Taylor Walls | L | FF | FF | FF | FF | SL |
| Ben Williamson (bench option) | R | FF | FF | FF | CU | CU |
| Cedric Mullins (bench option) | L | FF | FF | FC | FF | FC |
| Jorge Mateo (bench option) | R | FF | FF | FF | SL | SL |
| Nick Fortes (bench option) | R | FF | FC | FF | SL | FC |
| Ryan Vilade (bench option) | R | FF | FF | FC | FF | FC |

**Pitch key:** FF = four-seam fastball; FC = cutter; CU = curveball; SL = slider.

## How much to trust this

The expanded dataset has 44,981 unique usable pitches from 2025–26. All 30 player-season downloads reconcile with MLB physical pitch counts. Two rounds compared profile/context features with added prior-pitch sequence features, across two chronological development folds. The sequence gain was small; most improvement is not evidence of a special learned pitch order.

On the new postseason test, XGBoost transition log loss improved 1.75% over the contextual baseline (1.65625 vs. 1.68572); 1,348 pitches in 11 games. Miz's own test is only 182 pitches in two games. Aggregate postseason results were publicly known before evaluation. The forecast model was then refit on all pregame observations; it has no independent new test.

The planner minimizes approximate terminal wOBA plus a declared 0.0001 pitch-usage cost, with correct count changes and two-strike foul loops. It does not maximize whiffs alone. A walk, HBP, or damaging contact carries a terminal cost. These are weighted PA outcomes, not actual predicted runs or an expected score.

Actions require at least 50 season pitches by Miz against the relevant side and at least five uses in his last four outings. Count-level options generally need five observations. Individual batter/pitch samples are reported in game_plan.json and count_policies.csv. Same-day and future measurements do not enter the history features.

Observed pitch choice and execution are confounded. This model does not know intended location, catcher calls, hitter adaptation, or how Miz feels during warmups. It cannot establish that these branches outperform his actual strategy. Tiny model gaps are not meaningful proof of a preferred pitch. Use the alternative column to preserve options rather than repeating a deterministic script.

## Files and updates

- game_plan.json: all 14 batter cards, support, weights, alternatives, and probabilities.
- count_policies.csv: every supported count/previous-pitch branch.
- miz_regular_vs_postseason_shape.csv: observed velocity, spin, movement, and extension by pitch.
- selection.json and metrics.json: development rounds and locked postseason evaluation.
- forecast_contexts.csv and forecast.joblib: scored scenarios and saved forecast model.

Official game/lineup feed: [https://statsapi.mlb.com/api/v1/game/849805/boxscore](https://statsapi.mlb.com/api/v1/game/849805/boxscore). Roster and schedule snapshots are stored under data/processed/matchup/. Data cutoff is October 20; refresh availability and the batting order before game time.
