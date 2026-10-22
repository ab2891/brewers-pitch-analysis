# Misiorowski–Rays matchup experiment — October 21, 2026

Goal: a provisional, count-dependent Game 1 pitch plan, not proof of an optimal
sequence. MLB lists Jacob Misiorowski for October 23 at American Family Field.
The official lineup is not yet confirmed. Cover all active Rays hitters and mark
any latest-lineup order as provisional.

Freeze this design before inspecting new pitch-level postseason outcomes:

- Acquire 2025–26 pitches for active Rays hitters and Misiorowski, through October
  20 only. Include regular season and postseason, exclude exhibitions, validate
  identities, keys, date bounds, and physical pitch counts against MLB logs.
- Deduplicate overlapping pitcher/batter downloads by game/at-bat/pitch key.
- Development folds: train through May 31, validate June 1–July 15; then train
  through July 15, validate July 16–September 27. Earlier 2025 observations are
  training history. The previously scored regular-season holdouts are development
  data now and must not be presented as fresh evidence.
- Fresh outcome test: 2026 postseason pitches through October 20. Aggregate
  postseason results were already publicly known; pitch-level test predictions
  have not been inspected. Report this limited independence explicitly.
- Improvement round 1: context, batter identity, chosen pitch type, and prior-date
  pitcher/pitch physical profiles. Round 2: add consecutive previous pitch type
  and previous outcome. Compare depths 2 and 3 using mean development log loss.
  Fit encoding on each training fold only. Do not tune against postseason results.
- Predict pitch transitions: ball, strike, whiff, foul, in-play out, single,
  extra-base hit, home run, HBP. Missing/unsupported outcomes are excluded and
  counted. Use strictly prior-date physical profiles and batter/pitch history;
  current pitch execution is unavailable before the decision.
- Compare global and smoothed contextual transition-frequency baselines. Report
  overall and Miz/Rays-specific test log loss, a paired game bootstrap interval,
  and support. Keep the simpler scorer if the model does not demonstrate an edge.
- After the locked evaluation, refit the selected architecture on all available
  pregame data for a clearly labeled forecast model. This is not another test.
- Limit actions to Miz's observed recent repertoire with at least 50 season pitches
  against the batter's side, and report batter-side pitch-type support. Switch
  hitters face the right-handed Miz as lefties. Unknown lineage/intent/health
  remains outside the model.
- A count-state planner may minimize approximate terminal wOBA using transition
  probabilities. State includes count and previous pitch/result; fouls with two
  strikes loop, three strikes end the PA, four balls walk. Report branch choices
  and close alternatives, never a guaranteed fixed sequence. Weights come from
  observed pregame Statcast woba_value, with definitions and assumptions saved.
- No claimed counterfactual/causal improvement: observed selection, location intent,
  execution, catcher strategy, fatigue, runners, and adaptation are not controlled.
  Any model ranking is provisional scouting support. A model's predictive accuracy
  does not establish that following its policy improves actual game outcomes.
