# Every-count matchup and expected runs prevented

Completed all 12 counts through 3–2 for 14 active Rays hitters and all 24 legal base/out states: **4,032 count situations**. Reachable previous-pitch/result context expands this to **44,688 history situations**, with **149,184 supported candidate comparisons**. Impossible histories, such as a previous strike at 0–0, are excluded.

Open the [interactive explorer](artifacts/miz_rays_20261023_v2/run_values/explorer.html) to choose the hitter, count, outs, runners, and previous pitch/result. It is self-contained and needs no server.

## The score

**ERPA is a project definition: Expected Runs Prevented Above Miz’s usual supported pitch mix.** It is not claimed as an established baseball acronym. The underlying standard concept is pitch run value: the change in run expectancy associated with a pitch.

For situation s and candidate a:

```text
ERV(s,a) = sum over outcomes: predicted probability × estimated batting run-expectancy change
ERPA(s,a) = ERV(s, Miz usual supported mix) − ERV(s,a)
ERPA per 100 = 100 × ERPA(s,a)
```

The target is Statcast `delta_run_exp`, with positive values favoring the batter. A negative expected batting delta favors the pitcher. Positive ERPA means the candidate projects to allow fewer runs than the stated reference mix. This is runs per next pitch; it is neither earned-run average nor the expected total runs in the game.

The source concept is [Statcast pitch run value](https://baseballsavant.mlb.com/leaderboard/swing-take?group=Pitcher) and the [CSV delta_run_exp definition](https://baseballsavant.mlb.com/csv-docs). The standard run-expectancy accounting is runs scored plus expectancy after minus expectancy before, described in [FanGraphs RE24](https://library.fangraphs.com/misc/re24/). This implementation averages observed pitch delta_RE by outcome/context; it does not reconstruct a new full-inning RE24 table.

## Baseline, coverage and objective

The reference is Miz’s observed 2026 pitch frequencies for the batter’s handedness and count, restricted and normalized to supported candidates. It is held the same across previous-pitch histories. The summary averages over reachable prior histories using his observed frequencies; exact-history comparisons are also exported. A single supported pitch has ERPA zero and no runner-up claim.

All candidates share the same run-value weights at a given count/base/out situation. Their values differ through predicted outcome probabilities. Each comparison includes the runner-up gap, observed pitch support, and the fraction of forecast probability relying on sparse run-impact cells. The expected ERPA of the reference mix itself is exactly zero.

This ranks **immediate next-pitch run value**, using historical run-expectancy continuation. It differs from the earlier optimized approximate terminal-wOBA sequence objective; recommendations can change. The original model and outputs are preserved in the original run directory.

## Worked example: Caminero, 0–0, bases empty, no outs

| Pitch | Expected batting run change | ERPA vs usual mix, runs/pitch | ERPA runs/100 | Miz count/hand sample |
|---|---:|---:|---:|---:|
| FF | +0.00253 | +0.00249 | +0.249 | 211 |
| CU | +0.00703 | -0.00201 | -0.201 | 10 |
| FC | +0.00877 | -0.00375 | -0.375 | 49 |
| SL | +0.01158 | -0.00656 | -0.656 | 49 |

The usual supported mix projects +0.00502 batting runs/pitch here. The leading candidate projects +0.00253, a difference of +0.00249 runs/pitch. The per-100 number is a rescaling across equivalent situations, not guaranteed runs saved in this game.

## Every count: bases empty, no outs

Each cell shows the top point-estimate pitch and ERPA runs/100 versus the supported usual mix. These are history-averaged summaries, not a fixed pitch order. All other runner/out contexts and exact histories are in the explorer and CSVs.

| Hitter | 0–0 | 0–1 | 0–2 | 1–0 | 1–1 | 1–2 | 2–0 | 2–1 | 2–2 | 3–0 | 3–1 | 3–2 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Yandy Díaz | FC (+0.29) | FF (+0.32) | FF (+0.58) | FC (+0.77) | FC (+0.49) | FF (+0.49) | FF (+0.00) | FC (+0.85) | FF (+0.39) | FF (+0.00) | FF (+0.00) | SL (+0.48) |
| Jonathan Aranda | FC (+0.12) | FF (+0.24) | FF (+0.34) | FC (+0.41) | FC (+0.22) | FF (+0.40) | FC (+0.46) | FC (+0.17) | FF (+0.28) | FF (+0.00) | FF (+0.00) | FC (+0.53) |
| Liam Hicks | FC (+0.19) | FF (+0.34) | FF (+0.38) | FC (+0.66) | FC (+0.61) | SL (+0.51) | FC (+0.90) | FC (+0.63) | SL (+0.95) | FF (+0.00) | FF (+0.00) | SL (+1.69) |
| Junior Caminero | FF (+0.25) | CU (+0.44) | CU (+0.60) | FF (+0.06) | CU (+0.58) | CU (+0.77) | FF (+0.00) | SL (+0.24) | CU (+1.29) | FF (+0.00) | FF (+0.00) | CU (+1.87) |
| Chandler Simpson | FF (+0.37) | FF (+0.64) | FF (+0.25) | FF (+0.28) | FF (+0.63) | FF (+0.26) | FF (+0.02) | FF (+0.20) | SL (+0.25) | FF (+0.00) | FF (+0.00) | SL (+0.35) |
| Victor Mesa Jr. | FF (+0.21) | FF (+0.14) | FF (+0.27) | FF (+0.09) | FC (+0.23) | FF (+0.31) | FF (+0.10) | FC (+0.24) | FF (+0.13) | FF (+0.00) | FF (+0.00) | CU (+0.37) |
| Jonny DeLuca | FF (+0.11) | FC (+0.19) | SL (+0.41) | FC (+0.35) | FC (+0.45) | SL (+0.58) | FF (+0.00) | FC (+0.78) | SL (+0.79) | FF (+0.00) | FF (+0.00) | CU (+2.00) |
| Richie Palacios | FF (+0.10) | SL (+0.23) | SL (+0.72) | FC (+0.41) | FC (+0.45) | SL (+0.95) | FC (+0.55) | SL (+0.95) | SL (+1.21) | FF (+0.00) | FF (+0.00) | SL (+2.89) |
| Taylor Walls | FF (+0.15) | FF (+0.33) | FF (+0.51) | FC (+0.12) | SL (+0.21) | FF (+0.61) | FC (+0.33) | SL (+0.75) | SL (+0.85) | FF (+0.00) | FF (+0.00) | SL (+2.04) |
| Ben Williamson | FF (+0.25) | FC (+0.15) | CU (+0.77) | FF (+0.08) | FC (+0.32) | CU (+0.93) | FF (+0.00) | FC (+0.64) | CU (+0.97) | FF (+0.00) | FF (+0.00) | SL (+2.42) |
| Cedric Mullins | FC (+0.26) | FC (+0.37) | FF (+0.07) | FC (+0.70) | FC (+0.59) | SL (+0.22) | FC (+1.04) | FC (+0.97) | SL (+0.65) | FF (+0.00) | FF (+0.00) | SL (+1.73) |
| Jorge Mateo | FF (+0.11) | CU (+0.11) | SL (+1.02) | SL (+0.09) | SL (+0.26) | SL (+1.26) | FF (+0.00) | SL (+0.64) | SL (+1.41) | FF (+0.00) | FF (+0.00) | SL (+2.94) |
| Nick Fortes | FF (+0.30) | FC (+0.37) | SL (+1.09) | FF (+0.12) | FC (+0.55) | SL (+1.32) | FF (+0.00) | FC (+0.70) | SL (+1.42) | FF (+0.00) | FF (+0.00) | SL (+2.57) |
| Ryan Vilade | FF (+0.10) | FF (+0.06) | FF (+0.20) | FC (+0.41) | FC (+0.24) | FF (+0.10) | FF (+0.00) | SL (+0.61) | CU (+0.51) | FF (+0.00) | FF (+0.00) | SL (+1.69) |

FF = four-seam fastball; FC = cutter; CU = curveball; SL = slider. A +0.00 cell can reflect a single supported candidate; consult candidate_count before treating that as evidence.

## Limits and diagnostic

Run-impact means are estimated from the acquired 2025–26 matchup cohort, using a fixed smoothing pseudo-count of 20. Sparse full cells borrow from larger count/outcome and base/out/outcome groups. Unobserved cells retain full_cell_n = 0 rather than invented sample support. This is not a complete league RE288 estimate.

The version 2 transition model uses outs and occupancy of first, second and third as pre-pitch probability inputs. These states change predicted outcome probabilities as well as the run-value translation. Baserunning and execution can also affect the observed delta_RE within an outcome group. Location intent, catcher calls, adaptation, and selection effects are not causally controlled.

A diagnostic on the previously scored postseason set gives run-value RMSE 0.21575, versus 0.21579 for a constant mean. This retrospective diagnostic does not establish action-ranking accuracy or causal runs saved. The sample was already used, so this is not new independent validation and was not used for tuning.

The outcome model’s predictive evidence does not validate these action-level differences or policy improvements. No causal confidence interval is claimed. Tiny runner-up gaps and low candidate support should remain close options, not instructions. Do not sum ERPA across mutually exclusive scenarios.

## Files and reproduction

```bash
MATCHUP_RUN=artifacts/miz_rays_20261023_v2 .venv/bin/python src/score_erpa.py
MATCHUP_RUN=artifacts/miz_rays_20261023_v2 .venv/bin/python src/build_erpa_report.py
```

- [Interactive explorer](artifacts/miz_rays_20261023_v2/run_values/explorer.html)
- [4,032 count/base/out summaries](artifacts/miz_rays_20261023_v2/run_values/count_summary.csv)
- [Candidate values and outcome contributions](artifacts/miz_rays_20261023_v2/run_values/count_candidates.csv.gz)
- [Reachable-history candidate values](artifacts/miz_rays_20261023_v2/run_values/history_candidates.csv.gz)
- [Reachable-history summaries](artifacts/miz_rays_20261023_v2/run_values/history_summary.csv.gz)
- [Run-impact means and actual support counts](artifacts/miz_rays_20261023_v2/run_values/run_value_weights.csv)

## Contact history and development comparison

Pitch-specific contact-history inputs were tested on chronological development folds but did not improve log loss. The selected model uses runners and outs; the contact audit is descriptive and is not a manual penalty on the cutter. Mean development log loss: 1.63740; original model: 1.63747. Lower is better.

See [pitch contact audit](artifacts/miz_rays_20261023_v2/PITCH_DAMAGE_AUDIT.md).
