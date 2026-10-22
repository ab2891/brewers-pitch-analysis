# Repaired-data evaluation protocol

Frozen October 21, 2026, before fitting the repaired-data candidates or inspecting
September 22–27 test outcomes. The prior experiment's August/September test period
is now development data; it is not a fresh test.

- Regular-season Milwaukee pitches; all actual season pitching participants,
  including position players. Reconcile physical pitch counts against MLB logs.
- Train through August 1. Validate August 2–September 21. Test September 22 onward
  through the end of the regular season (six team games). Whole games stay together.
- Pre-pitch context, candidate pitch type, consecutive previous observed pitch,
  and optional history summarized strictly before the current calendar date.
  History includes earlier observed outcomes and delivered-pitch measurements,
  never the current pitch's measurements or same-day/future outcomes.
- Main outcome: batting-side run-expectancy change. Compare training mean,
  smoothed count/pitch/hand mean, and three regularized XGBoost regressors.
  Candidate depths/child weights/lambda: (2, 50, 20), (3, 50, 20), (4, 100, 30).
  Use learning rate .03, at most 1000 rounds, and validation early stopping at 50.
- Auxiliary outcome: whiff per pitch (not conditional on swing). Compare a
  training-frequency baseline and regularized XGBoost classifiers with the same
  three capacity settings; select on validation log loss. This outcome describes
  one pitch property and is not a substitute for overall run value.
- Select candidates solely on validation; record selection before test scoring.
  Keep the fitted training model rather than refitting after observing test results.
- Report test error and a paired whole-game bootstrap interval. Six games are a
  small test: results are preliminary and do not prove optimal pitch choice.
- No further tuning against this final period. If XGBoost does not beat the simple
  baseline, report that result and retain the simpler model as the preferred score.

History is available only from the acquired pitcher cohort, not all MLB. Online
evaluation can use outcomes from strictly earlier dates, including earlier test
dates, as they would be known before the next day's games. This is declared
sequential evaluation, not training on future labels.
