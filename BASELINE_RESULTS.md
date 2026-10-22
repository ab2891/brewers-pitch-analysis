# First XGBoost baseline — October 21, 2026

Historical result before data repair. See [RESULTS.md](RESULTS.md) for the current
repaired-data evaluation and [COMPLETENESS_AUDIT.md](COMPLETENESS_AUDIT.md) for
completed acquisition checks.

The training and scoring pipeline runs successfully, but the first XGBoost model
does not demonstrate an improvement over a simple training-average prediction on
the held-out test period.

The model predicts the batting side's pitch-level change in run expectancy
(`delta_run_exp`), using pre-pitch context, chosen pitch type, pitcher identity,
and a consecutive previously observed pitch. Lower estimates favor the pitcher.
It uses 18,716 Milwaukee regular-season pitches after removing known discrepant
pitcher-games and rows without a target or pitch classification.

| Split | Pitches | Dates |
|---|---:|---|
| Training | 12,862 | March 26–August 1, 2026 |
| Validation | 2,826 | August 2–26, 2026 |
| Test | 3,028 | August 27–September 20, 2026 |

| Model | Validation RMSE | Test RMSE |
|---|---:|---:|
| Training average | 0.21602 | 0.21480 |
| Smoothed contextual average | 0.21701 | 0.21634 |
| XGBoost | 0.21584 | 0.21492 |

XGBoost was selected using validation alone, stopping at iteration 86. Its test
error is slightly higher than the training-average baseline. The 95% paired
game-bootstrap interval for RMSE improvement is approximately [-0.00040, 0.00020],
which includes zero. This does not establish predictive skill beyond the baseline.

The data remains incomplete, ends September 21, and is not a full-season census.
Missing-game bias is not captured by the bootstrap. Alternative pitch estimates
are exploratory associations, constrained to training-supported repertoires; they
do not prove the best pitch or quantify causal benefit.

The complete saved run is in
[artifacts/20261022T032426279224Z/REPORT.md](artifacts/20261022T032426279224Z/REPORT.md).
The directory uses UTC; the run occurred on October 21 in Los Angeles. It includes
metrics, source hashes, package versions, saved encoder/model, held-out predictions,
per-pitcher metrics, and feature importances. Generated artifacts and data are
ignored by Git; this summary remains in the project.

Next: repair and reconcile acquisition, then establish an evaluation design for
new experiments before adding richer prior-history features. Preserve this test
result rather than repeatedly tuning against it.
