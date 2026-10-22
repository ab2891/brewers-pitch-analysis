# Brewers pitch analysis plan

Reviewed September 22, 2026 against the pasted conversation, README, downloader,
saved data, and local process list. This is the revised plan; pending changes below
have not yet been implemented unless noted in the progress update below.

## Full active staff vs Rays: October 21, 2026

The staff extension lives in `artifacts/brewers_rays_20261023_staff/` and preserves
all Miz-only versions. All 13 active Brewers pitchers and 14 current Rays hitters
are included. Fifty-four audited player-season files reconcile pitch counts;
deduplication leaves 75,930 usable observations. Handedness is pitcher-specific,
including switch hitters. Separate supported repertoires, histories and usual
pitch-mix baselines keep each pitcher's rankings independent.

The pooled model compares shape/base/out inputs, added pitcher identity, and
added strictly prior-date pitcher contact history on the same chronological
regular-season folds. The development selection and already-seen postseason
diagnostics are recorded separately; no new independent evaluation is claimed.
The explorer loads one pitcher's compressed data at a time, ranks each supported
candidate and explains ERPA by outcome. Individual sheets show opening choices
and conditional ball/called-strike branches rather than a fixed script.

See `STAFF_RAYS_GAME_PLAN.md` and `ERPA_GUIDE.md`. Active rosters are not a final
World Series availability guarantee. The snapshot's schedule still lists Game 1
on October 23; a last-game assumption was not used to fabricate completed games.
ERPA is relative to each pitcher's own mix and cannot rank relievers by ability.
Expected-run rankings also do not optimize win probability or bullpen deployment.

## Earlier runner/out probability extension: October 21, 2026

Version 2 under `artifacts/miz_rays_20261023_v2/` includes outs and separate
first/second/third-base occupancy indicators in the transition model and scores
each legal base/out context separately. The explorer explicitly ranks supported
pitches and displays hit, home-run and whiff probabilities and a contact audit.
The original model and output directory are preserved.

Two chronological regular-season development folds compare the original,
base/out, and base/out-plus-contact-history variants. Mean log loss is 1.637470,
1.637396, and 1.638065 respectively. The base/out model wins by a tiny margin;
the contact-history candidate is rejected. No cutter penalty is manually imposed.
The known October sample is retrospective diagnostic data and was not used for
selection. New independent validation of version 2 and action rankings remains
outstanding. The San Diego outing supports concern about the cutter that day,
while its season contact results are better; see the versioned damage audit.

## Original every-count run-value extension: October 21, 2026

All 12 counts through 3–2 and 24 base/out states are scored for the 14 active Rays
hitters. Legal previous-pitch histories over the eligible repertoire are included,
even if a rare previous choice would not be proposed as the next action. Future
candidate pitches remain subject to the existing support gate.

ERPA is explicitly project-defined as expected runs prevented relative to Miz's
usual supported pitch mix by handedness/count. Predicted outcome probabilities
are multiplied by pooled observed Statcast delta_run_exp values for the current
count/base/out/outcome. Outputs include candidate values, baseline values,
runner-up gaps, outcome contributions, and actual cell/action/history support.
No wOBA-to-run conversion is passed off as observed run expectancy.

The transition probabilities remain frozen and omit base/out inputs; base/out
context changes valuation only. The derived run-value diagnostic on previously
scored postseason data is essentially tied with a constant baseline. This remains
experimental forecast reasoning, not validated causal runs saved. See
ERPA_MATCHUP.md and its self-contained interactive explorer.

## Matchup extension completed: October 21, 2026

The Rays/Misiorowski request is implemented under MATCHUP_PROTOCOL.md, with two
development rounds comparing pre-pitch profiles against added sequence features.
Thirty audited player-season downloads supply 44,981 usable 2025–26 pitches.
The locked new postseason test contains 1,348 pitches in 11 games; transition log
loss improves 1.75% over the contextual baseline. Sequence features add only a
small gain. Miz's own test subset is two outings, so this is preliminary evidence.

The selected architecture is refit on all pregame data through October 20 for
forecasting, and a count/previous-pitch planner produces conditional batter cards
for all 14 active Rays hitters. It accounts for walks, strikeouts, fouls, and
contact costs instead of maximizing whiffs alone. Its objective is approximate
terminal wOBA, and the model-derived policy is not causally validated. Most opening
pitch values are near ties, with alternatives reported. The upcoming lineup is
unconfirmed; starter and lineup are refreshed when the planning command runs.

See MIZ_RAYS_GAME_PLAN.md and MATCHUP_RESULTS.md. Do not continue tuning against
the new postseason test. Further development needs a new evaluation design.

## Repair completed: October 21, 2026

This update supersedes the earlier acquisition status and next-action notes below.
The pitcher query now uses `pitchers_lookup[]` and `type=details`, with actual
inclusive date bounds. The old ignored filter returned league-wide responses at
a 25,000-row cap; this explains the systematic gaps. All data has been downloaded
again with verified checkpoints and atomic writes, and the original files are
archived in `data/archive/pre_repair_2026/`.

The regular-season cohort now includes all 34 pitching participants, including the
three missing players. All 162 Brewers games and 23,650 physical Milwaukee pitches
reconcile against the schedule and MLB pitching logs. All 64 previously missing
appearances are restored. There are no remaining missing appearances or pitch-count
discrepancies. Automatic balls/strikes are retained as events but excluded from
physical pitch counts. Re-running acquisition reproduced the raw file hashes.

The repaired modeling sample has 23,619 pitches. Prior-date history features and
three regularized candidates per outcome were evaluated under the frozen
EVALUATION_PROTOCOL.md, with September 22–27 held out as six fresh games.
The main run-value model still fails to beat a simple average on test, so its
scorer falls back to that average and withholds alternative pitch rankings.
An auxiliary whiff-per-pitch model improves test log loss by about 2.09% over a
constant-frequency baseline and has test ROC AUC 0.611. Its paired-game improvement
interval over the contextual baseline is positive, but six games are preliminary.

Acquisition, saved-model scoring, and the acceptance gate work end to end. See
RESULTS.md and COMPLETENESS_AUDIT.md. Further work should acquire independent
seasons and broader opponent histories; do not keep tuning against this final
test period. Optimal pitch choice remains a separate causal research question.

## Progress update: October 21, 2026

The overnight download was audited: all 31 files are present, but 64 regular-season
pitcher appearances are absent and 77 present appearances have count discrepancies.
See COMPLETENESS_AUDIT.md. Acquisition repairs and backfill remain pending.

An exploratory XGBoost training and scoring workflow is now implemented. It uses
the frozen existing data, excludes known discrepant pitcher-games, and requires
`--allow-incomplete`. It defaults to actual Milwaukee regular-season pitches,
using pitching team per game rather than roster labels. The first run has 18,716
usable pitches and chronological train/validation/test splits. Training-only
encoding, simple baselines, consecutive prior-pitch features, saved models,
per-pitcher evaluation, and a paired game bootstrap are included.

The first XGBoost model did not improve on the training-average baseline on the
held-out test period. See BASELINE_RESULTS.md. This establishes a runnable research
baseline, not a validated pitch recommendation system. Do not tune further against
the same test results. Repair data coverage next; expanded features or model
selection need a new evaluation protocol with an untouched final test set.

## Verified starting point

- The downloader process was running at review time (PID 25558). Process presence
  does not establish that requests are progressing or that the download will finish.
- The roster snapshot contains 31 unique pitcher IDs, including Kyle Harrison.
- One pitcher CSV is saved: Grant Anderson (681982), 904 rows spanning March 7
  through September 6. All rows have the expected pitcher ID; all pitch keys are
  present and unique. Its game types are 67 `S` rows and 837 `R` rows.
- Metadata requests March 1 through September 21, 2026. It is written before the
  download finishes, so it is not a completion record. Observed first/last pitch
  dates alone cannot prove or disprove full coverage.
- Code contains pitcher filtering, three request attempts, seven-day chunks, and
  deduplication by game, at-bat, and pitch number. Endpoint filtering and date-bound
  semantics were reported tested in the handoff but were not retested in this review.

## 1. Make acquisition safe to resume

Before a restart, fix the existing-file branch: `pitcher.player_name` accesses a
dictionary as an object and will raise an AttributeError. Use the dictionary key.
Keep the current process under observation; avoid launching a competing download.

Replace file-existence-only skipping with validated completion records scoped to
pitcher, season, requested dates, and query settings. Record successful empty
windows separately from failed requests. Write files atomically and checkpoint
completed windows so an interruption does not lose an entire pitcher's progress.
Preserve already validated data while repairing incomplete coverage.

Implement actual command-line arguments for season, start/end dates, chunk size,
and output directory; `parse_args()` currently only returns defaults. Pass chunk
size explicitly rather than reading global `args`. Freeze this acquisition's date
range so resuming on another day does not silently change the study window.

Validate CSV schema, source pitcher ID, date range, and nonempty pitch keys before
accepting a window. Reject malformed/error responses even if HTTP status is 200.
Check endpoint date behavior with boundary examples and defensively enforce the
requested inclusive dates in returned rows. Count rejected rows and duplicates;
flag conflicting duplicate records rather than silently replacing them.

Record per-window status, row count, actual UTC timestamp, and query parameters.
Retry transient failures with bounded backoff and leave persistent failures
explicitly incomplete. Do not overwrite prior provenance on resume.

Acceptance: offline checks cover existing-file resume, interruption recovery,
empty versus failed windows, wrong-pitcher rows, missing keys, and date boundaries;
a small live query confirms the endpoint contract before a new full run.

## 2. Define the analysis population

Use 2026 regular-season MLB pitches through the frozen cutoff for the initial
analysis. Preserve raw game types, but exclude spring training from this cohort.
The current saved file demonstrates that this filtering is necessary.

Distinguish pitchers on the roster snapshot from pitches actually thrown for
Milwaukee. Validate the season's participant list against historical appearances,
including traded/released players and any position-player pitching if the claim is
to cover all team pitches. Keep other-team appearances separately labeled.

Treat Kyle Harrison as a focal comparison player, not automatically an independent
control. `get_roster()` appends his comparison entry and deduplicates by ID, which
can overwrite a roster entry. Preserve team membership and comparison membership
as separate fields and verify his overlap with the Brewers cohort.

## 3. Finish and audit the dataset

Produce a per-pitcher audit with requested/successful/failed windows, row counts,
observed date ranges, game types, pitcher identity, missing required fields, and
duplicate/conflicting keys. Reconcile participation and game coverage against an
independent MLB appearance source; no pitches in a window can be legitimate.

Do not call the acquisition complete merely because every existing CSV parses.
Every expected pitcher/window must have either validated data or a verified empty
result. Preserve a versioned raw snapshot and create a separate processed dataset.
Add Git ignore rules for `.venv/` and generated raw/processed data before publishing
the project; no project `.gitignore` was present at review time.

## 4. Establish a descriptive and predictive baseline

First summarize pitch mix, usage by count and handedness, sample sizes, and missing
data. Define the outcome and its sign convention explicitly before fitting a
model. Choose a target available across the intended pitch population; do not
silently treat unavailable outcome fields as zero.

Separate two questions:

- Outcome prediction: how well can observed pitch characteristics explain or
  predict the recorded outcome?
- Pre-pitch choice evaluation: given information available before release, which
  available pitch types have promising estimated outcomes?

Realized location, velocity, movement, and release point describe the delivered
pitch. They must not enter a pre-pitch decision model as if already known. Use
strictly lagged summaries for those features when needed. Likewise, use pre-pitch
score/count/base state and prior pitches only for sequence features.

Use chronological train/validation/test splits with whole games kept together.
Fit preprocessing and player summaries on training history only. Compare simple
baselines before adding sequence features. Evaluate familiar-pitcher forecasting
separately from generalization to held-out pitchers, and report uncertainty and
sample size alongside performance.

## 5. Explore pitch-choice estimates only after validation

An observed-outcome model does not identify the counterfactual outcome of an
unthrown pitch. Pitch selection is confounded by pitcher ability, repertoire,
opponent, execution, and unobserved intent. Initially describe results as
associations or model-based estimates, not proof of the optimal pitch.

Restrict candidate pitches to each pitcher's repertoire established from prior
data. Check support for pitcher/context/pitch combinations and abstain where
samples are insufficient. Assess calibration and uncertainty before ranking
choices. Treat causal claims or policy recommendations as a later research stage
requiring explicit assumptions and stronger evaluation.

## Handoff and next action

The immediate next task is to check download progress and implement acquisition
repairs before restarting, then build the audit. Modeling follows the data gate.
Keep this plan and audit summaries in the project so a future session can resume
from verified state. Phone connectivity is a separate setup task; copying a
conversation does not establish access to this workspace.
