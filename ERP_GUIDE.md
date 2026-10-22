# ERP: Expected Runs Prevented

**ERP is the expected reduction in batting run expectancy on the next pitch.**
It puts the forecast on the pitcher's side of the ledger:

```text
ERP = −expected batting run change
```

Higher is better. Positive ERP means an expected decrease in the batting team's
scoring opportunity; negative ERP means an expected increase. Negative values
are retained, not clipped to zero. This is our project's forecast definition,
not an official MLB statistic or a measurement of causal runs saved.

This replaces the old mix-relative ERPA as the primary score in the staff
explorer and reports. **Improvement over usual mix is a separate comparison.**
The probability forecasts and pitch rankings do not change with this update.

## What can a single pitch prevent?

Run expectancy measures future scoring opportunity in a state. A runner on third
with nobody out presents a different opportunity from empty bases with two outs.
The count matters too: a ball at 3–2 has different consequences from one at 0–0.

Run-value accounting includes runs scored immediately and the change in future
scoring opportunity:

```text
batting run change = runs scored on the pitch + RE(after) − RE(before)
ERP = RE(before) − E[runs scored on the pitch + RE(after)]
```

A strike can reduce scoring opportunity without retiring the hitter. A walk can
increase it without a hit. A home run's scored runs still count even though the
bases clear. Expectancy after the third out is zero. This is the established
run-expectancy accounting described by
[FanGraphs](https://library.fangraphs.com/misc/re24/).

The implementation uses recorded Statcast `delta_run_exp` as its batting-side
target. See the [CSV field definitions](https://baseballsavant.mlb.com/csv-docs)
and [Statcast run-value background](https://baseballsavant.mlb.com/leaderboard/swing-take?group=Pitcher).
We estimate an expected pitch value from those observations; we do not reproduce
the official leaderboard or infer a literal number of runs that would otherwise
certainly have scored.

## How the model calculates ERP

First, forecast probabilities for nine outcome groups: ball, called/other strike,
swinging miss, foul, in-play out/choice, single/error, double/triple, home run and
hit by pitch. Their probabilities sum to one.

The pre-pitch inputs include hitter, actual batting side, pitcher throwing hand,
count, runners, outs, previous pitch and result, and proposed pitch type.
Historical pitch profiles and batter/pitch history use only prior dates.
The selected staff model also includes pitcher identity and lagged contact-damage
history, chosen on chronological regular-season development folds. It shares
information across pitchers while using separate pitcher profiles and arsenals.
It is not a separate sparse model fitted to each reliever.

Switch hitters bat opposite the selected pitcher's throwing hand. Historical
velocity, spin, movement and extension belong to that particular pitcher and
candidate pitch. Measurements of the unthrown future pitch are not available
and do not enter the forecast as if already known.

Next, estimate each outcome's average batting run impact at this count, runner
state and out state. The implementation pools observed `delta_run_exp` from the
acquired 2025–26 cohort. Sparse cells borrow information from broader count/outcome
and base/out/outcome groups with a fixed smoothing strength of 20. Unobserved
cells retain zero direct observations; smoothing does not manufacture support.

Finally, average those impacts using the forecast probabilities and negate:

```text
Expected batting run change = Σ P(outcome | situation, pitch) × run impact
ERP = Σ P(outcome | situation, pitch) × (−run impact)
```

The explorer's explanation table shows the nine terms in that last sum. Strikes
and outs can contribute positively, while walks and damaging contact can offset
them. More whiffs alone do not guarantee the highest ERP. The contributions sum
to ERP, apart from display rounding.

These are acquired-cohort run-value estimates, not a newly reconstructed
full-league run-expectancy matrix. The broad out group includes fielder's choices,
sacrifices and double plays. Their actual run impact enters the weights, but
pooling them limits advancement-risk precision. The single group includes reaches
on fielding error; displayed hit/reach probability is not strictly official hit
probability. Location intent and specific baserunning decisions are not modeled.

## ERP and improvement over usual mix are different

ERP does **not** subtract a pitcher's personal baseline. The separate comparison
does:

```text
ERP(usual mix) = Σ usual pitch frequency × ERP(pitch)
Improvement over usual mix = ERP(candidate) − ERP(usual mix)
```

The reference frequencies come from that pitcher's own observed 2026 usage
against this batting side at this count, restricted and normalized to supported
candidate pitches. They are held fixed across previous-pitch histories.

Here is an illustrative example, not a forecast from the fitted model:

| Pitch | Usual frequency | Expected batting run change | ERP, runs/pitch | ERP/100 | Improvement over mix/100 |
|---|---:|---:|---:|---:|---:|
| Fastball | 60% | −0.010 | +0.010 | +1.00 | +1.20 |
| Slider | 40% | +0.020 | −0.020 | −2.00 | −1.80 |

The usual mix has ERP `0.60 × 0.010 + 0.40 × (−0.020) = −0.002` runs/pitch.
The fastball's ERP is +0.010, while its improvement over that mix is
`0.010 − (−0.002) = +0.012`. Those are different questions and different numbers.

A pitch can improve over a weak mix and still have negative ERP. With only one
supported candidate, improvement over the mix is zero, but ERP can still be
positive or negative. The reference's weighted **improvement** is zero by
construction; its weighted **ERP** is generally not zero. The best available
candidate need not have positive ERP. If every option is negative, the leading
pitch is the smallest predicted increase in scoring opportunity.

## Reading the tables

Ranks sort by highest ERP, equivalently lowest expected batting run change.
The gap behind #1 is a direct candidate-to-candidate difference in the same
situation. Small gaps remain close options: the interface uses 0.001 runs/pitch
as a display heuristic, not a statistical confidence interval.

ERP's unit is **runs per next pitch**. Multiplying by 100 makes small differences
easier to read. ERP +0.010 becomes +1.00 per 100 equivalent situations. It does
not mean one pitch prevents a full run or that a 100-pitch outing will prevent
one run: counts, hitters, runners, execution and available choices keep changing.
Do not add all table rows together; they are mostly mutually exclusive scenarios.

The average-history view weights reachable histories of the eligible repertoire
using that pitcher's observed count/hand frequencies. The exact-history view
conditions the forecast on the selected previous pitch and result. It is not
a fixed pitch script. Recompute after each result.

Candidates require at least 50 season pitches overall, 20 against the batting
side and three in the latest four outings. At a count, at least five observed
pitches against that side are required. If none pass the count gate, only the
most-used otherwise eligible pitch remains, flagged as a fallback. Excluded
pitches are unranked, not declared worse. Samples pool across runner/out states;
they are not direct support for every exact situation.

Unlike personal-mix improvement, ERP uses a common run-value scale. Comparisons
between pitchers are mathematically like-for-like only for the same hitter,
count, runners, outs and history, under the same valuation. They still do not
establish an overall pitcher ability rating or decide who should enter the game.

## What ERP does not establish

ERP is not ERA, a save statistic, expected earned runs, total inning runs prevented
or win probability. It includes changes in scoring opportunity, not just runs
that actually score on this pitch. Inherited runners affect the situation; the
score is not a rule for assigning earned-run responsibility.

Pitch choice and execution are observational. Intent, catcher calls, location,
opposing scouting and selection effects remain uncontrolled. Forecasting an
unthrown pitch does not measure what would causally happen if the pitcher switched
to it. Low action/history support further limits confidence.

Model selection uses chronological regular-season development folds. October
results have already been inspected and are retrospective diagnostics, not an
independent final test. Better observed-outcome prediction does not prove that
following the action rankings will prevent runs.

The objective is expected run change rather than winning the game. Avoiding one
immediate run in a tied ninth inning can require different priorities from
minimizing average damage. Fatigue, health, real-time command, times through the
order, substitution rules and opponent adaptation are not fully represented.
The tool does not optimize bullpen deployment or establish game availability.

The source snapshot ends October 20, 2026. All 14 active Rays hitters are included,
not a confirmed nine-player batting order. Active roster membership is not a
guarantee of final World Series eligibility or availability.

## Export names and older reports

Current staff exports use `erp_runs_per_pitch` and `erp_runs_per_100`.
`usual_mix_erp_runs_per_pitch` is the weighted reference ERP, and
`improvement_over_usual_mix_runs_per_pitch` / `_per_100` are the separate comparison.

Legacy `erpa_runs_per_pitch` and `erpa_runs_per_100` columns retain their original
mix-relative meaning for compatibility. They are **not ERP**. Older Miz-only
reports retain the historical ERPA definition; the current staff explorer and
matchup sheets use ERP. No model retraining or probability changes are needed
for this score-definition update.
