# Understanding ERPA in this project

**Historical definition.** The current staff explorer uses **ERP = Expected Runs
Prevented**, the negative expected batting run change. Read [ERP_GUIDE.md](ERP_GUIDE.md)
for the current score. This document explains the older mix-relative ERPA, now
shown separately as “improvement over usual mix.”

ERPA means **Expected Runs Prevented Above the pitcher's usual supported pitch
mix**. It asks: *In this exact matchup and situation, how much lower is the
predicted batting run value of this pitch than the predicted value of this same
pitcher's usual choices?*

This is our project's name and definition, not an official MLB statistic or a
claim that this acronym has a standard baseball meaning. The established ideas
underneath it are run expectancy and pitch run value.

## Why a pitch can have a value measured in runs

Run expectancy is the average future scoring associated with a game state.
An empty base with two outs presents a different scoring opportunity from loaded
bases with nobody out. At the pitch level, the ball-strike count matters too:
a ball at 3–2 and a ball at 0–0 have different consequences.

Run-value accounting charges or credits an event for runs that score immediately
and the change in future scoring opportunity:

```text
batting run change = runs scored on the event
                   + run expectancy after
                   − run expectancy before
```

A strike can lower scoring expectation without ending the plate appearance.
A walk can increase it without producing a hit. A homer can score runs and clear
the bases; those scored runs still count. Expectancy after the third out is zero.
Positive batting run change favors the hitter; negative favors the pitcher.
See [FanGraphs' run-expectancy accounting](https://library.fangraphs.com/misc/re24/).

Our implementation uses the recorded Statcast `delta_run_exp` target. Savant
defines it as a pitch's change in run expectancy in its
[CSV documentation](https://baseballsavant.mlb.com/csv-docs).
The [Statcast run-value leaderboard](https://baseballsavant.mlb.com/leaderboard/swing-take?group=Pitcher)
is background for the established pitch-run-value concept. Our forecast and
baseline are separate project calculations, not a reproduction of that leaderboard.

## Step 1: predict a distribution, rather than one outcome

For a proposed pitch, the model estimates probabilities of ball, called/other
strike, whiff, foul, in-play out group, single/error group, double/triple, home run,
and hit by pitch. The probabilities sum to one. A pitch's value includes the bad
outcomes as well as its strikeout potential.

Inputs available before the pitch include hitter, actual batting side, pitcher
throwing hand, count, runners, outs, previous pitch/result, proposed pitch type,
and strictly prior-date pitch profiles and batter/pitch history. The selected
staff model may also use pitcher identity and lagged contact-damage history;
the recorded development selection determines that, not a manual adjustment.
Switch hitters bat opposite the pitcher's throwing hand in the forecast.

Pitch shape means historical velocity, spin, movement and extension for the
particular pitcher and candidate pitch. We do not feed the unthrown pitch's
future measured location or velocity into the prediction as if already known.
The staff shares one fitted statistical model, but each pitcher receives separate
profiles, repertoires, support checks, forecasts and reference mixes. Sharing data
avoids trying to fit a large independent model from one reliever's tiny sample.

## Step 2: translate that distribution into expected run value

For each count, runner state, out state and outcome, we estimate its average
recorded batting run change from the acquired 2025–26 cohort. Sparse cells borrow
information from broader count/outcome and base/out/outcome groups using a fixed
20-observation smoothing strength. A missing cell still has zero direct
observations; smoothing does not invent support.

Multiply each outcome's probability by its estimated run impact, then add:

```text
ERV(s, pitch) = Σ outcome probability(s, pitch) × run impact(s, outcome)
```

Here `s` includes the hitter, pitcher, count, runners, outs and selected history.
**ERV is expected batting run change on the next pitch. Lower is better for the
pitcher.** It is not the expected total runs in the inning, the hitter's eventual
wOBA, ERA, or the probability of winning the game. Historical continuation is
already represented in the run-value target; we do not add future pitches again.

The weights are estimated from this acquired matchup cohort, not every MLB pitch.
This is an outcome-associated run-value translation, not a newly reconstructed
full-league run-expectancy matrix. The broad in-play out group includes fielder's
choices, sacrifices and double plays. Their observed run impact enters the
weights, but pooling them still limits the model's advancement-risk precision.
The single group also includes reaches on fielding error, so the displayed
hit/reach probability is not strictly a forecast of official batting average.

## Step 3: define the comparison pitch mix

The reference is **this pitcher's own observed 2026 pitch frequencies against the
hitter's batting side at this count**, restricted to supported candidate pitches
and renormalized to sum to one. It is not Miz's mix for every pitcher, a league
average, a replacement pitcher, or an equal mix unless the reference has no
observed count support.

For example, if supported fastballs and sliders were used 60% and 40% of the time:

```text
reference ERV = 0.60 × fastball ERV + 0.40 × slider ERV
ERPA(pitch)   = reference ERV − pitch ERV
```

That same reference mix is used across previous-pitch histories at a given
pitcher/hand/count. The exact-history view conditions the probabilities on the
chosen previous pitch and result. The average-history view averages those
probabilities using that pitcher's observed frequencies over reachable histories
of the eligible repertoire, with equal weights only if none were observed.
It does not average every hypothetical history equally by default.

Candidates require at least 50 season pitches overall, 20 against the relevant
batting side, and three in the latest four outings. At a count, candidates also
require five observed pitches against that side. If none pass that final count
gate, only the most-used otherwise eligible pitch is retained and flagged as a
fallback. The interface reports support and does not infer that excluded pitches
are bad. With one candidate, ERPA is zero because the pitch is its own baseline.

## A worked example with units

These numbers are illustrative, not a forecast from the fitted model:

| Pitch | Reference frequency | ERV, batting runs/pitch | ERPA, runs/pitch | ERPA per 100 |
|---|---:|---:|---:|---:|
| Fastball | 60% | −0.010 | +0.012 | +1.20 |
| Slider | 40% | +0.020 | −0.018 | −1.80 |

The reference value is `0.60 × (−0.010) + 0.40 × 0.020 = +0.002`.
The fastball's ERPA is `+0.002 − (−0.010) = +0.012` runs per pitch.
Across 100 equivalent decisions, that difference rescales to 1.20 expected runs.
It does **not** mean this one pitch saves 1.20 runs or that a 100-pitch outing
will save that many runs: hitters, counts, runners, execution and opportunities
change throughout an actual game.
Do not add scores across all table rows or all counts: most rows describe
mutually exclusive alternatives, not pitches that will all occur.

Positive ERPA means better than the reference, zero means equal, and negative
means worse. Positive ERPA need not imply a negative batting ERV: a pitch can
still be the less damaging option among several unfavorable choices. The
reference mix's own average ERPA is exactly zero. The best candidate must be at
least as good as the weighted average of those same candidates; a positive
winner alone is therefore not evidence that the model works.

## Reading the ranking and the explanation table

Ranks sort by the lowest ERV. Because all candidates in the same comparison share
one reference, this also sorts by the highest ERPA. The gap behind #1 is a direct
difference between candidates, which is usually more useful than ERPA alone when
choosing between the first two pitches. Tiny gaps are marked as close options,
using a display heuristic of 0.001 runs/pitch; that is not a confidence interval.

For any selected candidate the explorer shows the arithmetic outcome by outcome:

```text
ERPA contribution = (reference outcome probability − candidate probability)
                  × outcome run impact
```

The nine contributions sum to ERPA, apart from display rounding. This reveals
whether a pitch leads because of fewer balls, more whiffs, fewer homers, or other
changes. A better whiff rate can be outweighed by walks or damaging contact.

**Do not rank different pitchers by their ERPA alone.** A +0.010 ERPA relative to
one pitcher's weak reference can be less attractive than a +0.003 ERPA relative
to another's strong reference. Expected batting ERV is the common run-value scale
for the same hitter/state, but choosing a reliever also requires availability,
fatigue, health, lineup position, substitution rules and performance uncertainty.
This tool does not optimize bullpen deployment.

## What the numbers do and do not establish

These are observational model estimates. Pitchers do not choose pitches randomly;
intent, location, catcher calls, opposing scouting and execution can affect both
the choice and outcome. Predicted value for an unthrown pitch is not measured
causal runs saved. Low action or history support makes that comparison less
credible even if the displayed probability is numerically precise.

Model features and rounds are chosen on chronological regular-season development
folds. October results have already been inspected in earlier work, so they are
retrospective diagnostics, not a fresh independent test. Predicting observed
outcomes better than a baseline does not validate a policy that switches pitches.

The objective is expected runs, not win probability. In a tied ninth inning,
avoiding one immediate run can matter more than minimizing average multi-run
damage; this model does not optimize that late-game objective. It also does not
model planned locations, real-time fatigue, times through the order or opponent
adaptation. Use it as a matchup aid with support and uncertainty visible, and
recompute after each pitch rather than following a fixed unresponsive sequence.

The current source snapshot ends October 20, 2026. Active roster membership is
not a guarantee of final World Series eligibility or availability for a game.
All 14 current Rays hitters are covered rather than represented as a confirmed
nine-man batting order.
