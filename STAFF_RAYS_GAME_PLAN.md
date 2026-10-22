# Brewers pitchers vs Rays: individual matchup sheets

13 pitchers, 14 hitters, 52,416 count/base/out situations and 1,456,344 supported exact-history candidate comparisons.

Open http://localhost:8765/explorer.html for ranked pitches at every count, runner/out state and reachable previous history. Read [the ERP guide](ERP_GUIDE.md) for the full definition and calculation.

Source cutoff: **2026-10-20**. Forecast context date: 2026-10-23. Active-roster membership is not a guarantee of final game eligibility, health or availability. The source schedule lists Game 1 on October 23; no last-game result or confirmed batting order is assumed.

These tables use **bases empty, no outs**. Openers and two-strike choices average this pitcher’s observed reachable histories; the called-strike and ball branches condition on the recommended opener and that actual result. They are next-pitch rankings, not a fixed script or a proven optimal sequence. **ERP = −expected batting run change**, displayed in runs per 100 equivalent decisions. Positive means an expected reduction in run expectancy; negative means an increase. The separate improvement over usual mix is not ERP. A `*` means only one supported pitch; ERP can still be nonzero, but no alternative comparison is available.

Shared model: pitcher_identity_damage; mean regular-season development log loss 1.63936. October has already been inspected and is used only for retrospective diagnostics. No new independent action-policy validation is claimed.

## Aaron Ashby (LHP)

Supported arsenal across batting sides: Changeup, Curveball, Sinker, Slider. Source-season pitches: 1,741. Last recorded appearance: 2026-10-15; latest four outings: 124 pitches. These records do not establish game availability.

| Rays hitter | Bats | 0–0 opener (ERP/100) | If opener called strike | If opener ball | 0–2 (ERP/100) | 3–2 (ERP/100) |
|---|---|---|---|---|---|---|
| Ben Williamson | R | SI (+1.62) | SI (+1.18) | SI (+2.57) | CH (+0.64) | SI (+1.29) |
| Cedric Mullins | L | SI (+0.49) | SI (+0.62) | SI (+1.02) | SL (+1.48) | SL (+0.73) |
| Chandler Simpson | L | SI (+1.28) | SI (+0.88) | SI (+2.65) | SL (+0.73) | SI (+1.97) |
| Jonathan Aranda | L | SI (-0.14) | SI (-0.34) | SI (+0.20) | SL (-0.26) | SI (-0.68) |
| Jonny DeLuca | R | SI (+0.13) | SI (+0.03) | SI (+0.64) | CH (+0.00) | SI (+0.13) |
| Jorge Mateo | R | SI (+0.43) | SI (+0.55) | SI (+0.97) | CU (+1.98) | CU (+2.10) |
| Junior Caminero | R | SI (-0.01) | SI (-0.48) | SI (+0.40) | CH (-0.44) | SI (-1.20) |
| Liam Hicks | L | SI (+1.37) | SI (+0.92) | SI (+2.67) | SL (+1.03) | SI (+1.16) |
| Nick Fortes | R | SI (+1.62) | SI (+1.14) | SI (+3.00) | CH (+0.37) | SI (+1.90) |
| Richie Palacios | L | SI (+1.30) | SI (+0.65) | SI (+2.19) | SL (+1.52) | SI (+0.67) |
| Ryan Vilade | R | SI (+0.34) | SI (+0.41) | SI (+0.77) | CH (+0.28) | SI (-0.15) |
| Taylor Walls | R | SI (+1.11) | SI (+0.90) | SI (+1.99) | CH (+0.60) | SI (+1.47) |
| Victor Mesa Jr. | L | SI (+0.60) | SI (+0.73) | SI (+1.20) | SL (+1.54) | SI (+0.90) |
| Yandy Díaz | R | SI (+0.47) | SI (+0.41) | SI (+1.30) | SI (-0.47) | SI (+0.01) |

[Count summaries](artifacts/brewers_rays_20261023_staff/pitchers/676879/count_summary.csv) · [Ranked count candidates](artifacts/brewers_rays_20261023_staff/pitchers/676879/count_candidates.csv.gz) · [Exact-history candidate comparisons](artifacts/brewers_rays_20261023_staff/pitchers/676879/history_candidates.csv.gz)

## Abner Uribe (RHP)

Supported arsenal across batting sides: Sinker, Slider. Source-season pitches: 1,032. Last recorded appearance: 2026-10-14; latest four outings: 65 pitches. These records do not establish game availability.

| Rays hitter | Bats | 0–0 opener (ERP/100) | If opener called strike | If opener ball | 0–2 (ERP/100) | 3–2 (ERP/100) |
|---|---|---|---|---|---|---|
| Ben Williamson | R | SL (+0.76) | SL (+0.94) | SL (+0.91) | SL (+1.63) | SL (+2.88) |
| Cedric Mullins | L | SL (+0.84) | SL (+1.58) | SL (+1.18) | SL (+2.36) | SL (+3.20) |
| Chandler Simpson | L | SI (+0.50) | SI (+0.63) | SI (+1.60) | SL (+0.04) | SI (+0.99) |
| Jonathan Aranda | L | SL (+0.17) | SL (+0.60) | SL (+0.33) | SL (+1.76) | SL (+2.08) |
| Jonny DeLuca | R | SL (+0.24) | SL (+0.62) | SI (+0.54) | SL (+1.79) | SL (+1.89) |
| Jorge Mateo | R | SI (+0.93) | SL (+1.24) | SI (+1.70) | SL (+2.94) | SL (+3.88) |
| Junior Caminero | R | SI (-0.58) | SL (-1.23) | SI (-0.29) | SL (-0.30) | SL (-1.11) |
| Liam Hicks | L | SI (+0.04) | SL (+0.06) | SI (+0.60) | SL (+0.19) | SI (-0.75) |
| Nick Fortes | R | SI (+0.60) | SL (+0.91) | SI (+1.19) | SL (+2.04) | SL (+2.23) |
| Richie Palacios | L | SL (+0.47) | SL (+1.04) | SI (+0.74) | SL (+2.02) | SL (+2.64) |
| Ryan Vilade | R | SI (+0.31) | SL (+0.69) | SI (+0.79) | SL (+1.80) | SL (+1.62) |
| Taylor Walls | L | SL (+0.76) | SL (+1.19) | SL (+0.83) | SL (+1.69) | SL (+1.61) |
| Victor Mesa Jr. | L | SL (+0.38) | SL (+1.11) | SI (+0.58) | SL (+2.15) | SL (+2.34) |
| Yandy Díaz | R | SL (-0.09) | SI (-0.13) | SI (+0.58) | SL (-0.34) | SI (-0.52) |

[Count summaries](artifacts/brewers_rays_20261023_staff/pitchers/682842/count_summary.csv) · [Ranked count candidates](artifacts/brewers_rays_20261023_staff/pitchers/682842/count_candidates.csv.gz) · [Exact-history candidate comparisons](artifacts/brewers_rays_20261023_staff/pitchers/682842/history_candidates.csv.gz)

## Antonio Senzatela (RHP)

Supported arsenal across batting sides: Cutter, Four-seam fastball, Sinker. Source-season pitches: 1,190. Last recorded appearance: 2026-10-06; latest four outings: 49 pitches. These records do not establish game availability.

| Rays hitter | Bats | 0–0 opener (ERP/100) | If opener called strike | If opener ball | 0–2 (ERP/100) | 3–2 (ERP/100) |
|---|---|---|---|---|---|---|
| Ben Williamson | R | FF (+0.57) | FF (+0.11) | FF (+0.86) | FC (-1.34) | FF* (-1.10) |
| Cedric Mullins | L | FC (+0.39) | FC (+0.36) | FC (+0.67) | FC (-0.15) | FC (+0.06) |
| Chandler Simpson | L | FF (-0.06) | FF (-0.76) | FF (+0.70) | FF (-3.39) | FF (-1.67) |
| Jonathan Aranda | L | FF (-0.75) | FF (-0.68) | FF (-0.93) | FF (-1.11) | FC (-2.12) |
| Jonny DeLuca | R | FF (-0.28) | FF (-0.46) | FF (-0.18) | FF (-1.41) | FF* (-2.04) |
| Jorge Mateo | R | SI (+0.21) | FF (+0.02) | SI (+0.82) | FF (-0.65) | FF* (-0.69) |
| Junior Caminero | R | FC (-1.03) | FF (-1.70) | SI (-0.91) | FF (-2.39) | FF* (-3.17) |
| Liam Hicks | L | FC (+0.23) | FC (-0.85) | FC (+0.61) | FC (-2.64) | FC (-2.64) |
| Nick Fortes | R | FF (+0.46) | FF (+0.01) | FF (+0.82) | FC (-0.82) | FF* (-1.55) |
| Richie Palacios | L | FF (+0.01) | FF (-0.39) | SI (+0.10) | FF (-1.74) | FC (-2.22) |
| Ryan Vilade | R | FF (-0.22) | FF (-0.22) | SI (-0.02) | FF (-0.80) | FF* (-1.86) |
| Taylor Walls | L | FF (-0.11) | FF (+0.04) | SI (+0.01) | FF (-0.72) | FF (-1.62) |
| Victor Mesa Jr. | L | FF (+0.24) | FF (+0.29) | FF (+0.34) | FF (-0.37) | FF (-0.93) |
| Yandy Díaz | R | FC (+0.12) | FF (-0.57) | FC (+0.44) | FF (-1.12) | FF* (-1.97) |

[Count summaries](artifacts/brewers_rays_20261023_staff/pitchers/622608/count_summary.csv) · [Ranked count candidates](artifacts/brewers_rays_20261023_staff/pitchers/622608/count_candidates.csv.gz) · [Exact-history candidate comparisons](artifacts/brewers_rays_20261023_staff/pitchers/622608/history_candidates.csv.gz)

## Chad Patrick (RHP)

Supported arsenal across batting sides: Cutter, Four-seam fastball, Sinker. Source-season pitches: 1,730. Last recorded appearance: 2026-09-27; latest four outings: 67 pitches. These records do not establish game availability.

| Rays hitter | Bats | 0–0 opener (ERP/100) | If opener called strike | If opener ball | 0–2 (ERP/100) | 3–2 (ERP/100) |
|---|---|---|---|---|---|---|
| Ben Williamson | R | FC (+0.94) | FC (+1.07) | FC (+1.06) | FC (+0.52) | FC (+0.77) |
| Cedric Mullins | L | FC (+1.07) | FC (+1.52) | FC (+1.28) | FC (+1.12) | FC (+1.05) |
| Chandler Simpson | L | FC (+0.68) | FC (+0.16) | FC (+1.05) | FC (-1.86) | SI (-0.72) |
| Jonathan Aranda | L | FC (+0.17) | FC (+0.23) | FC (+0.15) | FC (+0.31) | FC (-0.02) |
| Jonny DeLuca | R | FC (+0.26) | FC (+0.40) | FC (+0.38) | FC (+0.18) | FC (+0.36) |
| Jorge Mateo | R | FC (+0.74) | FC (+1.12) | SI (+1.13) | FC (+1.21) | FC (+1.70) |
| Junior Caminero | R | FC (-0.68) | FC (-1.15) | FC (-0.72) | FF (-1.66) | SI (-2.17) |
| Liam Hicks | L | FC (+1.23) | FC (+0.83) | FC (+1.57) | FC (-1.03) | FC (-1.79) |
| Nick Fortes | R | FC (+0.81) | FC (+1.16) | FC (+1.03) | FC (+0.81) | FC (+0.80) |
| Richie Palacios | L | FC (+0.69) | FC (+0.87) | FC (+0.90) | FC (-0.27) | FC (-1.13) |
| Ryan Vilade | R | FC (+0.44) | FC (+0.53) | FC (+0.46) | FF (+0.16) | FC (-0.70) |
| Taylor Walls | L | FC (+0.56) | FC (+0.65) | FC (+0.58) | FF (+0.13) | SI (-0.60) |
| Victor Mesa Jr. | L | FF (+0.60) | FC (+0.92) | FC (+0.59) | FC (+0.56) | FC (+0.16) |
| Yandy Díaz | R | FC (+0.79) | FC (+0.56) | FC (+1.05) | FF (-0.12) | FC (-0.89) |

[Count summaries](artifacts/brewers_rays_20261023_staff/pitchers/694477/count_summary.csv) · [Ranked count candidates](artifacts/brewers_rays_20261023_staff/pitchers/694477/count_candidates.csv.gz) · [Exact-history candidate comparisons](artifacts/brewers_rays_20261023_staff/pitchers/694477/history_candidates.csv.gz)

## DL Hall (LHP)

Supported arsenal across batting sides: Changeup, Curveball, Sinker, Slider, Sweeper. Source-season pitches: 1,078. Last recorded appearance: 2026-10-14; latest four outings: 81 pitches. These records do not establish game availability.

| Rays hitter | Bats | 0–0 opener (ERP/100) | If opener called strike | If opener ball | 0–2 (ERP/100) | 3–2 (ERP/100) |
|---|---|---|---|---|---|---|
| Ben Williamson | R | SI (+1.63) | CU (+1.38) | SI (+2.57) | CU (+1.82) | CU (+1.74) |
| Cedric Mullins | L | SL (+0.81) | SL (+1.74) | SL (+1.17) | ST* (+0.39) | SI* (-0.49) |
| Chandler Simpson | L | SI (+1.36) | SL (+1.22) | SI (+2.68) | ST* (+0.71) | SI* (+1.13) |
| Jonathan Aranda | L | SI (+0.09) | SL (+0.48) | SI (+0.42) | ST* (+0.77) | SI* (-1.26) |
| Jonny DeLuca | R | CU (+0.69) | CU (+1.04) | CU (+0.98) | CU (+0.75) | CU (+0.64) |
| Jorge Mateo | R | CU (+0.91) | CU (+1.74) | CU (+1.12) | CU (+3.30) | CU (+4.80) |
| Junior Caminero | R | SI (+0.02) | CU (+0.27) | SI (+0.40) | CU (+0.98) | CU (+0.95) |
| Liam Hicks | L | SI (+1.37) | SL (+1.78) | SI (+2.66) | ST* (+0.01) | SI* (+0.33) |
| Nick Fortes | R | SI (+1.62) | CU (+0.78) | SI (+3.02) | CU (+0.73) | SI (+0.98) |
| Richie Palacios | L | SI (+1.35) | SL (+1.09) | SI (+2.24) | ST* (+0.12) | SI* (+0.05) |
| Ryan Vilade | R | CU (+0.62) | CU (+1.17) | SI (+0.84) | CU (+1.64) | CU (+1.39) |
| Taylor Walls | R | SI (+1.03) | CU (+0.97) | SI (+1.90) | CH (+0.76) | SI (+0.71) |
| Victor Mesa Jr. | L | SI (+0.65) | SL (+1.54) | SI (+1.24) | ST* (+0.81) | SI* (+0.06) |
| Yandy Díaz | R | CU (+0.73) | CU (+1.06) | SI (+1.25) | CU (+0.38) | CU (+0.46) |

[Count summaries](artifacts/brewers_rays_20261023_staff/pitchers/669084/count_summary.csv) · [Ranked count candidates](artifacts/brewers_rays_20261023_staff/pitchers/669084/count_candidates.csv.gz) · [Exact-history candidate comparisons](artifacts/brewers_rays_20261023_staff/pitchers/669084/history_candidates.csv.gz)

## Dustin May (RHP)

Supported arsenal across batting sides: Curveball, Cutter, Four-seam fastball, Sinker, Sweeper. Source-season pitches: 2,509. Last recorded appearance: 2026-10-15; latest four outings: 168 pitches. These records do not establish game availability.

| Rays hitter | Bats | 0–0 opener (ERP/100) | If opener called strike | If opener ball | 0–2 (ERP/100) | 3–2 (ERP/100) |
|---|---|---|---|---|---|---|
| Ben Williamson | R | FF (+1.54) | FF (+1.57) | FF (+1.86) | FF (+0.43) | SI (+1.33) |
| Cedric Mullins | L | SI (+0.82) | FF (+1.31) | SI (+1.38) | FF (+1.17) | SI (+1.27) |
| Chandler Simpson | L | FF (+1.44) | FF (+1.86) | SI (+2.38) | FF (+0.09) | SI (+2.99) |
| Jonathan Aranda | L | SI (+0.28) | FF (+0.44) | SI (+0.49) | FF (+0.49) | ST (+0.56) |
| Jonny DeLuca | R | FF (+0.64) | FF (+0.84) | SI (+0.92) | FF (+0.46) | SI (+1.49) |
| Jorge Mateo | R | SI (+1.47) | FF (+1.42) | SI (+2.31) | FF (+1.35) | SI (+2.39) |
| Junior Caminero | R | SI (-0.26) | FF (-0.52) | SI (+0.22) | FF (-0.57) | SI (-0.35) |
| Liam Hicks | L | FC (+0.81) | FF (+0.95) | SI (+1.28) | FF (-0.30) | SI (+1.07) |
| Nick Fortes | R | FF (+1.47) | FF (+1.45) | SI (+1.92) | FF (+0.17) | SI (+2.39) |
| Richie Palacios | L | FF (+0.80) | FF (+0.80) | SI (+1.14) | ST (+0.08) | SI (+0.78) |
| Ryan Vilade | R | SI (+0.61) | FF (+0.92) | SI (+1.22) | FF (+0.88) | SI (+0.71) |
| Taylor Walls | L | SI (+0.91) | FF (+1.18) | SI (+1.48) | FF (+0.99) | SI (+1.40) |
| Victor Mesa Jr. | L | FF (+1.04) | FF (+1.37) | FF (+1.10) | FF (+1.25) | FF (+0.91) |
| Yandy Díaz | R | SI (+0.48) | FF (+0.81) | SI (+1.38) | FF (+0.73) | SI (+1.18) |

[Count summaries](artifacts/brewers_rays_20261023_staff/pitchers/669160/count_summary.csv) · [Ranked count candidates](artifacts/brewers_rays_20261023_staff/pitchers/669160/count_candidates.csv.gz) · [Exact-history candidate comparisons](artifacts/brewers_rays_20261023_staff/pitchers/669160/history_candidates.csv.gz)

## Jacob Misiorowski (RHP)

Supported arsenal across batting sides: Curveball, Cutter, Four-seam fastball, Slider. Source-season pitches: 2,829. Last recorded appearance: 2026-10-11; latest four outings: 294 pitches. These records do not establish game availability.

| Rays hitter | Bats | 0–0 opener (ERP/100) | If opener called strike | If opener ball | 0–2 (ERP/100) | 3–2 (ERP/100) |
|---|---|---|---|---|---|---|
| Ben Williamson | R | FF (+1.48) | FF (+1.61) | FF (+1.56) | CU (+1.31) | SL (+3.08) |
| Cedric Mullins | L | FC (+1.23) | SL (+1.89) | FC (+1.75) | SL (+2.51) | SL (+4.32) |
| Chandler Simpson | L | FF (+1.51) | FF (+2.14) | FF (+2.05) | FF (+0.46) | FC (+0.47) |
| Jonathan Aranda | L | FC (+0.54) | FF (+0.86) | FC (+0.89) | SL (+1.87) | SL (+3.15) |
| Jonny DeLuca | R | FF (+0.64) | FC (+0.98) | FC (+1.05) | SL (+1.37) | CU (+2.45) |
| Jorge Mateo | R | FF (+0.98) | SL (+1.55) | FC (+1.25) | SL (+2.91) | SL (+4.92) |
| Junior Caminero | R | FF (-0.19) | FF (-0.17) | FF (-0.16) | CU (+0.53) | CU (+0.72) |
| Liam Hicks | L | FC (+1.35) | FC (+1.07) | FC (+1.89) | SL (+0.32) | SL (-0.51) |
| Nick Fortes | R | FF (+1.33) | FC (+1.55) | FC (+1.54) | SL (+1.68) | SL (+2.47) |
| Richie Palacios | L | FC (+0.87) | SL (+1.23) | FC (+1.29) | SL (+2.03) | SL (+3.43) |
| Ryan Vilade | R | FC (+0.74) | FF (+0.97) | FC (+1.07) | SL (+1.53) | SL (+2.05) |
| Taylor Walls | L | SL (+0.87) | FF (+1.45) | FC (+1.11) | FF (+2.11) | SL (+2.64) |
| Victor Mesa Jr. | L | FF (+1.09) | FF (+1.66) | FC (+1.25) | FF (+2.54) | SL (+3.44) |
| Yandy Díaz | R | FC (+0.75) | FF (+0.70) | FC (+1.27) | FF (+0.94) | FC (-0.25) |

[Count summaries](artifacts/brewers_rays_20261023_staff/pitchers/694819/count_summary.csv) · [Ranked count candidates](artifacts/brewers_rays_20261023_staff/pitchers/694819/count_candidates.csv.gz) · [Exact-history candidate comparisons](artifacts/brewers_rays_20261023_staff/pitchers/694819/history_candidates.csv.gz)

## JoJo Romero (LHP)

Supported arsenal across batting sides: Changeup, Sinker, Sweeper. Source-season pitches: 1,004. Last recorded appearance: 2026-10-15; latest four outings: 82 pitches. These records do not establish game availability.

| Rays hitter | Bats | 0–0 opener (ERP/100) | If opener called strike | If opener ball | 0–2 (ERP/100) | 3–2 (ERP/100) |
|---|---|---|---|---|---|---|
| Ben Williamson | R | SI (+1.19) | ST (+1.36) | SI (+1.97) | ST (+1.87) | ST (+3.10) |
| Cedric Mullins | L | ST (+0.82) | ST (+1.45) | ST (+1.29) | ST* (+1.01) | ST* (+1.11) |
| Chandler Simpson | L | ST (+0.77) | ST (+1.32) | ST (+1.31) | ST* (+1.38) | ST* (+2.92) |
| Jonathan Aranda | L | ST (+0.25) | ST (+0.86) | ST (+0.59) | ST* (+1.23) | ST* (+1.35) |
| Jonny DeLuca | R | ST (+0.67) | ST (+1.33) | ST (+1.25) | ST (+1.62) | ST (+3.28) |
| Jorge Mateo | R | ST (+1.10) | ST (+1.82) | ST (+1.73) | CH (+1.45) | ST (+2.16) |
| Junior Caminero | R | ST (+0.09) | ST (+0.30) | ST (+0.54) | ST (+0.59) | ST (+1.62) |
| Liam Hicks | L | SI (+0.90) | ST (+0.56) | SI (+1.96) | ST* (+0.18) | ST* (-0.74) |
| Nick Fortes | R | SI (+1.03) | ST (+1.00) | SI (+2.09) | ST (+0.76) | SI (+0.91) |
| Richie Palacios | L | SI (+0.90) | ST (+0.41) | SI (+1.69) | ST* (+0.44) | ST* (-0.48) |
| Ryan Vilade | R | ST (+0.63) | ST (+1.17) | ST (+1.03) | ST (+0.61) | ST (+0.61) |
| Taylor Walls | R | ST (+0.87) | ST (+1.48) | SI (+1.78) | ST (+1.32) | ST (+1.92) |
| Victor Mesa Jr. | L | ST (+0.41) | ST (+1.16) | SI (+1.06) | ST* (+1.34) | ST* (+1.46) |
| Yandy Díaz | R | ST (+0.57) | ST (+0.90) | ST (+1.12) | ST (-0.14) | ST (+0.39) |

[Count summaries](artifacts/brewers_rays_20261023_staff/pitchers/668941/count_summary.csv) · [Ranked count candidates](artifacts/brewers_rays_20261023_staff/pitchers/668941/count_candidates.csv.gz) · [Exact-history candidate comparisons](artifacts/brewers_rays_20261023_staff/pitchers/668941/history_candidates.csv.gz)

## Kyle Harrison (LHP)

Supported arsenal across batting sides: Changeup, Four-seam fastball, Slurve. Source-season pitches: 2,106. Last recorded appearance: 2026-09-26; latest four outings: 113 pitches. These records do not establish game availability.

| Rays hitter | Bats | 0–0 opener (ERP/100) | If opener called strike | If opener ball | 0–2 (ERP/100) | 3–2 (ERP/100) |
|---|---|---|---|---|---|---|
| Ben Williamson | R | FF (+0.76) | SV (+0.10) | FF (+0.81) | SV (-0.02) | SV (-0.06) |
| Cedric Mullins | L | SV (-0.13) | SV (+0.47) | SV (+0.06) | SV (+0.43) | SV (-0.10) |
| Chandler Simpson | L | FF (+0.36) | SV (-0.31) | FF (+0.90) | SV (-1.09) | SV (+0.11) |
| Jonathan Aranda | L | SV (-0.34) | SV (-0.22) | SV (-0.40) | SV (-0.34) | SV (-1.27) |
| Jonny DeLuca | R | FF (-0.06) | SV (-0.44) | FF (-0.16) | SV (-0.48) | SV (+0.17) |
| Jorge Mateo | R | FF (+0.08) | SV (+0.20) | FF (+0.04) | SV (+0.95) | SV (+2.04) |
| Junior Caminero | R | SV (-0.63) | SV (-0.51) | SV (-0.54) | SV (-0.62) | SV (-0.68) |
| Liam Hicks | L | FF (-0.07) | SV (-0.48) | FF (-0.36) | SV (-0.66) | SV (-2.08) |
| Nick Fortes | R | FF (+0.47) | SV (-0.11) | FF (+0.47) | SV (-0.18) | SV (-0.87) |
| Richie Palacios | L | FF (+0.38) | FF (+0.16) | FF (+0.33) | SV (+0.13) | SV (-0.30) |
| Ryan Vilade | R | FF (-0.23) | SV (-0.25) | SV (-0.44) | SV (-0.22) | SV (-0.59) |
| Taylor Walls | R | FF (+0.02) | SV (+0.10) | SV (+0.04) | SV (+0.16) | SV (+0.36) |
| Victor Mesa Jr. | L | FF (-0.15) | SV (-0.01) | FF (-0.40) | SV (-0.04) | SV (-0.81) |
| Yandy Díaz | R | FF (-0.36) | SV (-0.78) | FF (-0.69) | SV (-1.24) | SV (-2.47) |

[Count summaries](artifacts/brewers_rays_20261023_staff/pitchers/690986/count_summary.csv) · [Ranked count candidates](artifacts/brewers_rays_20261023_staff/pitchers/690986/count_candidates.csv.gz) · [Exact-history candidate comparisons](artifacts/brewers_rays_20261023_staff/pitchers/690986/history_candidates.csv.gz)

## Logan Henderson (RHP)

Supported arsenal across batting sides: Changeup, Cutter, Four-seam fastball, Sweeper. Source-season pitches: 1,641. Last recorded appearance: 2026-10-12; latest four outings: 310 pitches. These records do not establish game availability.

| Rays hitter | Bats | 0–0 opener (ERP/100) | If opener called strike | If opener ball | 0–2 (ERP/100) | 3–2 (ERP/100) |
|---|---|---|---|---|---|---|
| Ben Williamson | R | FF (+1.62) | FF (+1.52) | FF (+1.86) | CH (+1.06) | FF (+0.98) |
| Cedric Mullins | L | FC (+1.15) | FC (+1.45) | FC (+1.65) | CH (+1.16) | CH (+0.26) |
| Chandler Simpson | L | FF (+1.00) | FF (+0.95) | FF (+1.67) | CH (+0.37) | CH (+1.02) |
| Jonathan Aranda | L | FC (+0.10) | FF (+0.29) | FC (+0.27) | FF (+0.10) | FF (-1.59) |
| Jonny DeLuca | R | FF (+0.58) | FF (+0.64) | FF (+0.54) | CH (+1.16) | CH (+1.76) |
| Jorge Mateo | R | FF (+0.85) | FF (+1.25) | FC (+1.01) | CH (+1.90) | CH (+2.29) |
| Junior Caminero | R | FF (-0.40) | FF (-0.62) | FF (-0.33) | CH (+0.03) | CH (-0.54) |
| Liam Hicks | L | FC (+1.12) | FF (+0.93) | FC (+1.72) | CH (-0.14) | FF (-1.06) |
| Nick Fortes | R | FF (+1.46) | FF (+1.27) | FF (+1.74) | CH (+1.50) | CH (+2.10) |
| Richie Palacios | L | FF (+0.88) | FF (+0.84) | FC (+1.01) | CH (+1.16) | CH (+0.13) |
| Ryan Vilade | R | FF (+0.52) | FF (+0.80) | FC (+0.70) | CH (+0.88) | CH (-0.19) |
| Taylor Walls | L | FF (+0.71) | FF (+1.08) | FC (+0.78) | CH (+1.47) | CH (+1.17) |
| Victor Mesa Jr. | L | FF (+1.14) | FF (+1.44) | FF (+1.26) | CH (+1.32) | FF (+0.64) |
| Yandy Díaz | R | FC (+0.88) | FF (+0.61) | FC (+1.43) | FF (+0.27) | FF (-0.70) |

[Count summaries](artifacts/brewers_rays_20261023_staff/pitchers/701656/count_summary.csv) · [Ranked count candidates](artifacts/brewers_rays_20261023_staff/pitchers/701656/count_candidates.csv.gz) · [Exact-history candidate comparisons](artifacts/brewers_rays_20261023_staff/pitchers/701656/history_candidates.csv.gz)

## Robert Gasser (LHP)

Supported arsenal across batting sides: Changeup, Cutter, Four-seam fastball, Sinker, Sweeper. Source-season pitches: 1,945. Last recorded appearance: 2026-10-14; latest four outings: 322 pitches. These records do not establish game availability.

| Rays hitter | Bats | 0–0 opener (ERP/100) | If opener called strike | If opener ball | 0–2 (ERP/100) | 3–2 (ERP/100) |
|---|---|---|---|---|---|---|
| Ben Williamson | R | SI (+1.13) | ST (+0.89) | SI (+1.96) | ST (+1.06) | ST (+2.35) |
| Cedric Mullins | L | FC (+0.58) | FC (+0.87) | FC (+0.84) | FF (+0.71) | ST (+0.11) |
| Chandler Simpson | L | FF (+0.59) | ST (+0.62) | SI (+1.70) | ST (+0.47) | ST (+2.26) |
| Jonathan Aranda | L | FC (+0.21) | ST (+0.07) | FC (+0.34) | ST (+0.44) | ST (+0.33) |
| Jonny DeLuca | R | FF (+0.48) | FF (+0.39) | FF (+0.44) | ST (+0.66) | ST (+2.16) |
| Jorge Mateo | R | FC (+0.89) | ST (+0.94) | FC (+1.22) | CH (+0.62) | CH (+2.24) |
| Junior Caminero | R | FC (+0.03) | FF (-0.74) | FC (+0.45) | FF (-0.51) | ST (+0.35) |
| Liam Hicks | L | SI (+1.00) | SI (+0.44) | SI (+2.32) | ST (-0.44) | SI (+1.65) |
| Nick Fortes | R | SI (+1.13) | ST (+0.61) | SI (+2.50) | ST (-0.03) | SI (+2.00) |
| Richie Palacios | L | SI (+0.85) | FF (+0.83) | SI (+1.68) | FF (+0.53) | SI (+0.55) |
| Ryan Vilade | R | FC (+0.35) | FF (+0.29) | FC (+0.64) | FF (+0.51) | FC (+0.51) |
| Taylor Walls | R | SI (+0.58) | ST (+0.60) | SI (+1.35) | ST (+0.46) | SI (+1.10) |
| Victor Mesa Jr. | L | FC (+1.03) | FC (+1.04) | FC (+1.54) | FF (+0.71) | SI (+0.54) |
| Yandy Díaz | R | FC (+0.36) | ST (+0.09) | FC (+0.77) | FF (-0.90) | SI (+0.04) |

[Count summaries](artifacts/brewers_rays_20261023_staff/pitchers/688107/count_summary.csv) · [Ranked count candidates](artifacts/brewers_rays_20261023_staff/pitchers/688107/count_candidates.csv.gz) · [Exact-history candidate comparisons](artifacts/brewers_rays_20261023_staff/pitchers/688107/history_candidates.csv.gz)

## Shane Drohan (LHP)

Supported arsenal across batting sides: Changeup, Curveball, Cutter, Four-seam fastball, Sinker, Slider. Source-season pitches: 2,026. Last recorded appearance: 2026-10-15; latest four outings: 116 pitches. These records do not establish game availability.

| Rays hitter | Bats | 0–0 opener (ERP/100) | If opener called strike | If opener ball | 0–2 (ERP/100) | 3–2 (ERP/100) |
|---|---|---|---|---|---|---|
| Ben Williamson | R | FF (+1.41) | SL (+1.45) | SI (+1.65) | SL (+1.90) | SL (+3.24) |
| Cedric Mullins | L | FC (+0.83) | FC (+1.46) | FC (+1.04) | SL (+1.73) | SL (+2.25) |
| Chandler Simpson | L | FF (+1.35) | FF (+0.96) | FF (+2.11) | SL (+0.56) | SL (+1.24) |
| Jonathan Aranda | L | FC (+0.51) | FC (+0.80) | FC (+0.72) | FF (+0.77) | SI (-1.19) |
| Jonny DeLuca | R | FF (+0.85) | FF (+0.94) | FF (+0.94) | SL (+1.27) | SL (+2.72) |
| Jorge Mateo | R | FC (+1.06) | SL (+1.57) | FC (+1.30) | SL (+2.72) | SL (+4.34) |
| Junior Caminero | R | FC (+0.43) | FC (-0.03) | FC (+0.73) | CH (-0.08) | SL (-0.54) |
| Liam Hicks | L | SI (+0.88) | SL (+1.12) | SI (+2.11) | SL (+0.90) | SL (+1.46) |
| Nick Fortes | R | SL (+1.24) | SL (+1.83) | SI (+2.26) | SL (+2.23) | SL (+3.53) |
| Richie Palacios | L | FF (+1.15) | FF (+1.40) | SI (+1.49) | SL (+1.49) | SL (+1.24) |
| Ryan Vilade | R | SL (+0.80) | SL (+1.34) | FC (+1.02) | SL (+1.75) | SL (+2.72) |
| Taylor Walls | R | FF (+0.71) | FF (+1.04) | FC (+0.99) | CH (+1.00) | SL (+0.22) |
| Victor Mesa Jr. | L | FC (+1.20) | FC (+1.51) | FC (+1.57) | SL (+1.63) | SL (+2.09) |
| Yandy Díaz | R | FC (+0.61) | FC (+0.03) | FC (+1.03) | FF (-0.50) | SI (-1.36) |

[Count summaries](artifacts/brewers_rays_20261023_staff/pitchers/675660/count_summary.csv) · [Ranked count candidates](artifacts/brewers_rays_20261023_staff/pitchers/675660/count_candidates.csv.gz) · [Exact-history candidate comparisons](artifacts/brewers_rays_20261023_staff/pitchers/675660/history_candidates.csv.gz)

## Trevor Megill (RHP)

Supported arsenal across batting sides: Four-seam fastball, Knuckle curve. Source-season pitches: 952. Last recorded appearance: 2026-10-14; latest four outings: 61 pitches. These records do not establish game availability.

| Rays hitter | Bats | 0–0 opener (ERP/100) | If opener called strike | If opener ball | 0–2 (ERP/100) | 3–2 (ERP/100) |
|---|---|---|---|---|---|---|
| Ben Williamson | R | FF (+1.78) | FF (+1.95) | FF (+2.36) | KC (+2.04) | KC (+3.81) |
| Cedric Mullins | L | FF (+0.89) | FF (+1.58) | FF (+1.10) | FF (+1.34) | FF* (+1.15) |
| Chandler Simpson | L | FF (+1.80) | FF (+2.26) | FF (+2.93) | KC (+0.96) | FF* (+2.44) |
| Jonathan Aranda | L | KC (+0.73) | KC (+1.16) | KC (+1.33) | KC (+1.80) | FF* (-0.20) |
| Jonny DeLuca | R | FF (+0.92) | FF (+1.28) | FF (+1.24) | KC (+1.68) | KC (+3.96) |
| Jorge Mateo | R | FF (+1.28) | FF (+1.87) | FF (+1.71) | KC (+2.53) | KC (+4.50) |
| Junior Caminero | R | FF (-0.19) | FF (-0.28) | FF (+0.20) | KC (+0.36) | KC (+1.49) |
| Liam Hicks | L | FF (+1.02) | FF (+1.30) | FF (+1.67) | KC (-0.17) | FF* (-0.07) |
| Nick Fortes | R | FF (+1.85) | FF (+1.92) | FF (+2.44) | KC (+1.88) | KC (+3.51) |
| Richie Palacios | L | FF (+1.10) | KC (+1.24) | FF (+1.39) | KC (+1.79) | FF* (-0.07) |
| Ryan Vilade | R | FF (+0.85) | FF (+1.29) | FF (+1.07) | FF (+1.23) | KC (+1.55) |
| Taylor Walls | L | FF (+0.90) | FF (+1.42) | FF (+1.16) | FF (+1.12) | FF* (+1.13) |
| Victor Mesa Jr. | L | FF (+1.38) | FF (+1.78) | FF (+1.68) | KC (+1.85) | FF* (+1.86) |
| Yandy Díaz | R | FF (+0.57) | FF (+0.93) | FF (+0.85) | FF (+0.87) | KC (+1.39) |

[Count summaries](artifacts/brewers_rays_20261023_staff/pitchers/656730/count_summary.csv) · [Ranked count candidates](artifacts/brewers_rays_20261023_staff/pitchers/656730/count_candidates.csv.gz) · [Exact-history candidate comparisons](artifacts/brewers_rays_20261023_staff/pitchers/656730/history_candidates.csv.gz)
