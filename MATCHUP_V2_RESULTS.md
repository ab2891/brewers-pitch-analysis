# Runner/out probability model and ranked explorer

The current explorer is at http://localhost:8765/explorer.html while the local
preview server runs. Its file is
`artifacts/miz_rays_20261023_v2/run_values/explorer.html`.
The original run is preserved in `artifacts/miz_rays_20261023/`.

Outs and separate occupancy indicators for each base now enter the XGBoost
outcome classifier before run valuation. Every supported next pitch is scored
separately for all 24 base/out states. Numbered rankings sort by lowest expected
batting run change, with the leader highlighted, the gap to alternatives, and
hit/home-run/whiff probabilities. The sample column pools Miz's season count/hand
observations across runner/out contexts; it is not support for an exact situation.

## Development comparison

The same two chronological regular-season folds compare three fixed candidates.
Lower average log loss is better:

| Candidate | Mean development log loss |
|---|---:|
| Original sequence model | 1.637470 |
| Add runners and outs | 1.637396 |
| Add runners, outs and lagged pitcher contact history | 1.638065 |

The selected model includes runners and outs. The difference from the original
is tiny; it should not be described as a substantial accuracy improvement.
Contact-history features were rejected on development scores. They excluded
current-date outcomes, used shrinkage, and included observed/expected contact
damage and hard-hit rates; no manual cutter penalty was applied.

The already-known October sample was not used for selection. Its retrospective
run-value RMSE is 0.215749, versus 0.215795 for a constant mean. This is not
independent evidence of improvement or reliable pitch-choice differences.
Action rankings remain observational point estimates.

## Cutter check

In the San Diego NLDS outing, 11 cutters produced three balls in play: two
hard-hit singles and an RBI fielder's choice. Mean exit velocity was 92.7 mph.
That concern is supported. Across the regular season, the cutter produced 70
balls in play, 11 hits, three homers and 22 hard hits, with 86.7 mph mean exit
velocity and .276 expected wOBA on contact. Those season results do not support
assuming every cutter is bad. The explorer includes the full pitch-by-pitch-type
audit with regular-season, NLDS and NLCS samples.

Fielder's choices remain grouped with other `out` outcomes in the classifier.
Their actual run impact is included in pooled Statcast run-value weights rather
than assigned zero. That broad grouping still limits advancement-risk modeling.

Example: Caminero at 0–0, empty bases, zero outs ranks **FF, CU, FC, SL**.
The fastball's projected advantage above the supported usual mix is 0.249 runs
per 100 equivalent pitches. This rescaling is not a game runs-saved projection.

## Verification

- All 24 unit tests pass, including prior-date exclusion, candidate-specific
  histories, runner occupancy parsing and count/continuation rules.
- All 4,032 count situations and 149,184 exact-history candidate comparisons
  have finite, normalized predictions and correctly ordered numerical ranks.
- Outcome probabilities respond separately to outs and runners. Across the
  generated inventory, the largest absolute changes were about 1.52 and 5.01
  percentage points, respectively. These are model sensitivities, not measured
  causal effects.
- Reference-weighted ERPA is zero within every candidate group; outcome
  contributions sum to ERPA, and gaps behind the best candidate are nonnegative.
- Chromium checked all 12 count controls in marginal and exact-history modes,
  runner/out selection, 14 hitter options and 12 contact-audit rows. No JavaScript
  errors occurred. Desktop and mobile layouts were rendered.

See [ERPA_MATCHUP.md](ERPA_MATCHUP.md) for formulas, assumptions and output links.
