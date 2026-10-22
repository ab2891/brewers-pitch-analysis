# Full Brewers staff vs Rays

The [staff explorer](http://localhost:8765/explorer.html) covers all **13 active
Brewers pitchers against 14 Rays hitters**, with numbered rankings for 12 counts
and all 24 runner/out states. This yields **52,416 count situations** and
**491,448 exact-history situations**, comparing **1,456,344 supported candidate
pitches**. The [individual matchup sheets](STAFF_RAYS_GAME_PLAN.md) show each
pitcher's repertoire, openers, conditional ball/called-strike branches and
two-strike choices. Read [ERP_GUIDE.md](ERP_GUIDE.md) for the full score definition.

The 13 pitchers are Aaron Ashby, Abner Uribe, Antonio Senzatela, Chad Patrick,
DL Hall, Dustin May, Jacob Misiorowski, JoJo Romero, Kyle Harrison, Logan
Henderson, Robert Gasser, Shane Drohan and Trevor Megill. This is the active
roster snapshot, not every pitcher who appeared for Milwaukee during the season
or a guarantee of final World Series eligibility or game availability.

## Data and model

Fifty-four player-season downloads reconcile physical pitches against official
MLB logs. Pitcher/hitter source overlaps are deduplicated and conflicting records
are rejected. The combined sample contains 75,930 usable 2025–26 pitch events.
The source snapshot ends October 20, 2026; no World Series results are included.
The schedule snapshot still lists Game 1 on October 23 rather than a final game.

One pooled XGBoost model shares statistical information while using separate
pitcher profiles, eligible repertoires, handedness, histories and reference pitch
mixes. Switch hitters change sides according to the selected pitcher's throwing
hand. Current-date history is excluded from each pre-pitch profile. Candidate
support gates and fallback cases are documented in the guide and explorer.

Two chronological regular-season development folds select features and training
rounds. All candidates include count, runners, outs, batter, historical pitch
shape, batter/pitch history, previous pitch/result and throwing/batting side.

| Staff candidate | Mean development log loss |
|---|---:|
| Base/out and pitch shape | 1.639761 |
| Add pitcher identity | 1.639553 |
| Add pitcher identity and lagged contact damage | **1.639365** |

The selected model uses 324 rounds. The added-feature advantage is small. This
selection differs from the Miz-only version because the training population has
expanded; it is not a manual change to lower the cutter's ranking.

## Retrospective diagnostic, not independent validation

The already-inspected October period contains 2,286 events across 17 games in the
expanded cohort. Outcome log loss is 1.635616 versus 1.651198 for the contextual
baseline. Projected run-value RMSE is 0.199662 versus 0.199931 for a constant mean.
The run-value difference is very small, and no new independent outcome or
pitch-choice-policy validation is claimed.

Per-pitcher samples are much smaller. Dustin May, Logan Henderson, Robert Gasser
and Shane Drohan do not beat the context baseline on their individual October
diagnostics. Chad Patrick and Kyle Harrison have no October observations in
this source snapshot. The explorer displays these sample sizes and results;
the pooled result does not establish reliable recommendations for each pitcher.

Rankings minimize immediate expected batting run change. They do not optimize
late-game win probability, location intent, bullpen use or fatigue. ERP is the negative expected batting run change, measured on a common scale
for the same hitter and state. Improvement over each pitcher's usual mix is
reported separately and is not directly comparable across pitchers as an ability
rating. Neither score alone establishes an overall pitcher ranking. Sparse actions, sparse histories,
pooled advancement outcomes and selection confounding remain material limits.

## Verification and files

All 28 unit tests pass. Generated-data checks verify coverage, correct pitcher and
batting side, legal prior histories, finite normalized probabilities, ordered
ranks, ERV arithmetic and ERP equal to negative expected batting run change and zero reference-weighted
improvement over usual mix within each comparison.
The full check is saved in
`artifacts/brewers_rays_20261023_staff/validation.json`.

Chromium loaded all 13 pitcher datasets, checked switch-hitter sides, exercised
all 12 counts in average and exact-history modes, changed runners/outs and
verified the score contribution arithmetic. There were no JavaScript errors.
Desktop and mobile layouts render without horizontal page overflow; wide tables
scroll inside their cards.

The staff explorer loads one compressed pitcher dataset at a time and needs
HTTP. The original Miz-only runs remain unchanged. Models, source hashes,
development selection, per-pitcher outputs and diagnostics are under
`artifacts/brewers_rays_20261023_staff/`. Source roster and schedule snapshots are
under `data/processed/staff_rays/`. Reproduction commands are in [README.md](README.md).

## ERP naming update

The current staff explorer, matchup sheets and exports use **ERP = Expected
Runs Prevented**, defined as the expected reduction in batting run expectancy
on the next pitch: `ERP = -expected_batting_run_delta`. This is a score-definition
change, not just a relabeling of the old ERPA. Saved predictions and pitch
rankings are unchanged. Improvement over usual mix remains a separate field.
ERP can be negative and need not be zero when only one pitch is supported.
Legacy `erpa_*` CSV columns retain their original mix-relative meaning for
compatibility; use the new `erp_*` columns for ERP.
