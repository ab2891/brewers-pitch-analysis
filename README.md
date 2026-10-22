# Brewers Pitch Analysis

**Current staff matchup:** [individual pitcher plans](STAFF_RAYS_GAME_PLAN.md),
[full ERP explanation](ERP_GUIDE.md), and
[staff explorer](artifacts/brewers_rays_20261023_staff/explorer.html).
See [staff results and verification](STAFF_RESULTS.md) for coverage and evidence.
The active-roster snapshot covers all 13 Brewers pitchers against 14 Rays hitters,
each with a separate supported repertoire, count/hand baseline and ranked plan.
Runners and outs enter the probability model as well as the run-value mapping.
The staff model pools data; it does not fit a separate sparse model per reliever.
**ERP (Expected Runs Prevented) = −expected batting run change on the next pitch.**
Higher is better; negative ERP means an expected increase in scoring opportunity.
Improvement over usual mix is a separate comparison. Legacy Miz-only reports
retain their original ERPA definition; the current staff reports use ERP.
World Series eligibility, health and game availability are not established by
active-roster membership.

```bash
# On a fresh checkout, create .venv and install requirements-lock.txt first
# (see Run below), then acquire the prerequisite matchup snapshot:
.venv/bin/python src/download_matchup.py
.venv/bin/python src/download_staff.py
# Train once; the command refuses to overwrite a fitted version:
.venv/bin/python src/staff_matchup.py train
.venv/bin/python src/staff_matchup.py score --forecast-date 2026-10-23
.venv/bin/python src/build_staff_report.py
python3 -m http.server 8765 --bind 127.0.0.1 --directory artifacts/brewers_rays_20261023_staff
```

Open http://localhost:8765/explorer.html in a browser. The staff explorer requires
HTTP and loads one compressed pitcher dataset at a time. The source snapshot is
frozen through October 20. All 54 player-season files reconcile physical pitch
counts to MLB logs; overlapping pitcher/hitter observations are deduplicated.
Model selection uses regular-season chronological development folds. October
diagnostics reuse previously inspected data and are not independent validation
of a pitch-choice policy. See the ERP guide for units, baselines and limits.
Generated explorers, datasets and fitted models are excluded from Git; artifact
links become available locally after acquisition, training and report generation.

**Earlier Miz-only run values:** [ERPA matchup report](ERPA_MATCHUP.md) and
[interactive situation explorer](artifacts/miz_rays_20261023_v2/run_values/explorer.html)
score all 12 counts through 3–2, all 24 base/out states, and legal prior-pitch
histories for 14 Rays hitters. ERPA is the project's expected runs prevented
relative to Miz's usual supported pitch mix. Positive values favor the pitcher.
The report explains the baseline, outcome contributions, support, and uncertainty.
Version 2 uses runners and outs inside the probability model, numbers the pitch
rankings, and shows hit/HR/whiff probabilities and a season-versus-postseason
[contact audit](artifacts/miz_rays_20261023_v2/PITCH_DAMAGE_AUDIT.md).
Contact-history features were evaluated but did not improve development log loss;
they are not used to manually penalize the cutter. Original artifacts remain intact.
This next-pitch run-value objective differs from the earlier approximate
terminal-wOBA sequence objective; neither establishes a causally optimal policy.

```bash
export MATCHUP_RUN=artifacts/miz_rays_20261023_v2
.venv/bin/python src/improve_matchup.py --forecast
.venv/bin/python src/score_erpa.py
.venv/bin/python src/build_erpa_report.py
python3 -m http.server 8765 --bind 127.0.0.1 --directory "$MATCHUP_RUN/run_values"
```

Open http://localhost:8765/explorer.html in a browser (opening the HTML source tab
in an editor does not render the explorer). Training provenance and selection are
in the version 2 run directory. `src/improve_matchup.py` trains a new version once
and refuses to overwrite an existing forecast. Postseason diagnostics reuse an
already-seen sample; they are not new independent validation.

**Earlier sequence model:** [Miz vs. Rays Game 1 plan](MIZ_RAYS_GAME_PLAN.md) and
[matchup model improvements](MATCHUP_RESULTS.md). The new opponent-specific
transition model uses 2025–26 data, two development rounds, and a new postseason
test. Its provisional count branches are distinct from the earlier unsupported
run-value regression below. The Game 1 batting order remains unconfirmed.

A reproducible Statcast acquisition and modeling workflow for Milwaukee's 2026
regular season. The acquisition gaps are repaired. The current whiff-per-pitch
model has a modest advantage on a fresh six-game test; the run-value model does
not, so its scoring command falls back to a simple baseline.

See [RESULTS.md](RESULTS.md) for findings and
[COMPLETENESS_AUDIT.md](COMPLETENESS_AUDIT.md) for coverage evidence.

## Run

The existing `.venv` has the required packages installed. For a fresh environment:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-lock.txt
```

```bash
.venv/bin/python src/download_statcast.py --season 2026 --start 2026-03-01 --end 2026-10-20
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python src/train_model.py
.venv/bin/python src/train_whiff.py
```

The downloader uses inclusive date bounds, `pitchers_lookup[]`, and `type=details`.
It decodes the CSV BOM, rejects malformed/wrong-pitcher/out-of-range rows, detects
conflicting pitch keys and response limits, retries request failures, and saves
verified date-window checkpoints. Re-running resumes those checkpoints and
reconciles every pitcher/game against current MLB game logs. It also checks the
team participant list and completed-game schedule. Metadata stays `in_progress`
until every check passes; CSV and JSON files are replaced atomically.

Downloads contain regular-season pitches for the season's actual Brewers pitching
participants, including position players, plus the comparison pitcher Kyle Harrison.
Their other-team appearances are retained in raw files. Modeling defaults to
actual Milwaukee pitches, identified by home/away side and inning half. Kyle's
comparison membership is stored separately from team membership.

Generated data and models are ignored by Git. The original data and audit are
preserved under `data/archive/pre_repair_2026/`. The archived first run is summarized
in [BASELINE_RESULTS.md](BASELINE_RESULTS.md); it is not the current result.

## Evaluation and interpretation

[EVALUATION_PROTOCOL.md](EVALUATION_PROTOCOL.md) fixes the evaluation design:
train through August 1, validate August 2–September 21, test September 22–27.
The previous test period is development data now. Each outcome selects among three
regularized XGBoost candidates using validation only, records the selection before
test scoring, and compares against constant and contextual baselines. Whole dates
and games stay together. A paired game bootstrap reports test uncertainty.

Inputs are pre-pitch count, runners, score difference, inning, handedness, pitcher,
candidate pitch type, and a consecutive prior pitch from the same plate appearance.
History summaries include strictly earlier dates' outcomes, velocity, spin,
extension, and release position. Current-pitch measurements/outcomes are excluded.
History is limited to the acquired pitcher cohort. Sequential evaluation uses
prior days' observations, including earlier test dates, as a live workflow would.

`train_model.py` predicts batting-side `delta_run_exp`, the change in run expectancy
across the pitch; lower favors the pitcher. `train_whiff.py` predicts the probability
of a whiff per pitch, not conditional on swinging. It counts `swinging_strike`,
`swinging_strike_blocked`, `missed_bunt`, and `swinging_pitchout` as whiffs. This
auxiliary outcome does not measure all aspects of run prevention.

The scoring acceptance gate requires XGBoost to win validation, beat both test
baselines, and have a positive lower bootstrap improvement bound. Otherwise the
scorer uses the validation-preferred simple baseline. The gate does not tune
hyperparameters against the test. Alternative run-value pitch rankings are withheld
when the gate fails. Any future rankings remain observational, not causal advice.

There are only six fresh test games. Do not keep tuning against them. Broader
claims need more independent seasons and opponents.

## Saved runs and scoring

Each training command prints a new `artifacts/<run>/` directory. It contains
`REPORT.md`, `metrics.json`, `selection.json`, an audit snapshot, saved encoder and
XGBoost model, baseline counts, held-out predictions, and prepared test contexts.
Run-value runs also contain per-pitcher metrics and feature importances. Whiff runs
include descriptive probability reliability bins.

```bash
.venv/bin/python src/predict.py --run artifacts/20261022T034528964225Z \
  --input artifacts/20261022T034528964225Z/test_contexts.csv \
  --output artifacts/run_value_scores.csv

.venv/bin/python src/predict.py --run artifacts/20261022T034640563564Z_whiff \
  --input artifacts/20261022T034640563564Z_whiff/test_contexts.csv \
  --output artifacts/whiff_scores.csv
```

Use prepared pre-pitch feature columns listed in the run's `metrics.json`.
`predict.py` returns the accepted `predicted_score`, the research XGBoost estimate,
and the scoring-model identity. Scoring new contexts requires accurate prior-date
history, not guessed or future-derived values. The exported contexts demonstrate
that schema. `examples/context.csv` is a minimal illustrative context for models
trained with `--feature-set base`; history models need the additional history fields.

For archived incomplete-data research, `train_model.py --allow-incomplete` enables
the explicit override after excluding flagged pitcher-games. It never repairs data
and cannot bypass an in-progress acquisition. Normal training needs no override.

## Source references

- [Statcast CSV field definitions](https://baseballsavant.mlb.com/csv-docs)
- [Pybaseball's pitcher query implementation](https://raw.githubusercontent.com/jldbc/pybaseball/master/pybaseball/statcast_pitcher.py)
- [XGBoost training and model persistence](https://xgboost.readthedocs.io/en/stable/python/python_intro.html)

Exact MLB source URLs, file hashes, and pitch-count conventions are stored in the
completeness audit. See [PLAN.md](PLAN.md) for the longer research plan.
