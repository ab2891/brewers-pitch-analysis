# Repaired-data results — October 21, 2026

The data gaps are repaired. The run-value model still has no demonstrated predictive advantage, while the auxiliary whiff model shows a modest improvement on six fresh games.

## Data and evaluation

All 162 Brewers regular-season games and 34 season pitching participants are covered; physical pitch counts reconcile exactly with MLB logs. The model uses 23,619 labeled, classified Milwaukee pitches. The 64 previously absent appearances are restored, and all remaining count discrepancies are resolved. Original source files are archived.

Training ends August 1; validation covers August 2–September 21; the fresh test is September 22–27 (818 pitches in six games). The old experiment’s test period is now development data. All candidate settings were frozen in [EVALUATION_PROTOCOL.md](EVALUATION_PROTOCOL.md) before the new test was scored.

History features use strictly earlier dates: observed pitcher and batter results plus pitcher velocity, spin, extension, and release summaries. The observations cover the acquired pitcher cohort, not all MLB. Current pitch execution and outcome are excluded. Validation selects among three regularized XGBoost candidates.

## Run value

| Model | Test RMSE |
|---|---:|
| Training-average baseline | 0.21016 |
| Smoothed contextual baseline | 0.21078 |
| XGBoost | 0.21096 |

XGBoost narrowly wins validation but loses on test. Its paired-game improvement interval includes zero. The scoring command therefore uses the training-average baseline; alternative run-value pitch rankings are withheld. This is a working research pipeline, not evidence of an optimal-pitch system.

## Auxiliary whiff probability

Whiff is defined per pitch, not conditional on a swing. It is an auxiliary outcome and does not replace overall run prevention.

| Model | Test log loss | Test Brier score | Test ROC AUC |
|---|---:|---:|---:|
| Training-frequency baseline | 0.35449 | 0.10083 | 0.500 |
| Smoothed contextual baseline | 0.35667 | 0.10144 | 0.547 |
| XGBoost | 0.34709 | 0.09929 | 0.611 |

XGBoost lowers log loss by 2.09% against the constant-frequency baseline. Against the contextual baseline selected on validation, the 95% paired-game improvement interval is [0.00379, 0.01640], favoring XGBoost. The whiff scorer passes the acceptance gate and returns the XGBoost probability.

The six-game test is small; the interval does not establish broad season-to-season reliability. Probability reliability bins are exported as diagnostics. Higher whiff probability alone does not imply a better pitch choice or lower expected runs.

## Saved outputs

- [Run-value report](artifacts/20261022T034528964225Z/REPORT.md)
- [Whiff report](artifacts/20261022T034640563564Z_whiff/REPORT.md)
- [Coverage audit](COMPLETENESS_AUDIT.md)
- Scored test contexts: `artifacts/repaired_run_value_scores.csv` and `artifacts/repaired_whiff_scores.csv`.
- Models, encoders, source hashes, audit snapshots, selection records, predictions, and probability reliability bins are saved under the corresponding run directories.

Generated artifacts are local and ignored by Git. See [README.md](README.md) for repeatable acquisition, training, and scoring commands.

## Next research step

Use additional independent seasons and broader opponent histories before trying to validate run-value pitch rankings. Keep this final test frozen: further tuning needs another evaluation design, not repeated optimization on these six games. The data repair and operational pipeline are complete; the run-value research result remains negative.
