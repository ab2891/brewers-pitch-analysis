# Brewers pitchers vs Rays: individual matchup sheets

13 pitchers, 14 hitters, 52,416 count/base/out situations and 1,456,344 supported exact-history candidate comparisons.

Open http://localhost:8765/explorer.html for ranked pitches at every count, runner/out state and reachable previous history. Read [the ERPA guide](ERPA_GUIDE.md) for the full definition and calculation.

Source cutoff: **2026-10-20**. Forecast context date: 2026-10-23. Active-roster membership is not a guarantee of final game eligibility, health or availability. The source schedule lists Game 1 on October 23; no last-game result or confirmed batting order is assumed.

These tables use **bases empty, no outs**. Openers and two-strike choices average this pitcher’s observed reachable histories; the called-strike and ball branches condition on the recommended opener and that actual result. They are next-pitch rankings, not a fixed script or a proven optimal sequence. ERPA is runs per 100 equivalent decisions above **this pitcher’s own supported usual mix**; it is not comparable across pitchers as an ability rating. A `*` means only one supported pitch and therefore ERPA zero.

Shared model: pitcher_identity_damage; mean regular-season development log loss 1.63936. October has already been inspected and is used only for retrospective diagnostics. No new independent action-policy validation is claimed.

## Aaron Ashby (LHP)

Supported arsenal across batting sides: Changeup, Curveball, Sinker, Slider. Source-season pitches: 1,741. Last recorded appearance: 2026-10-15; latest four outings: 124 pitches. These records do not establish game availability.

| Rays hitter | Bats | 0–0 opener (ERPA/100) | If opener called strike | If opener ball | 0–2 (ERPA/100) | 3–2 (ERPA/100) |
|---|---|---|---|---|---|---|
| Ben Williamson | R | SI (+0.54) | SI (+0.70) | SI (+1.24) | CH (+0.28) | SI (+1.58) |
| Cedric Mullins | L | SI (+0.18) | SI (+0.11) | SI (+0.32) | SL (+0.55) | SL (+0.47) |
| Chandler Simpson | L | SI (+0.53) | SI (+0.58) | SI (+0.89) | SL (+0.75) | SI (+1.39) |
| Jonathan Aranda | L | SI (+0.14) | SI (+0.15) | SI (+0.29) | SL (+0.18) | SI (+1.17) |
| Jonny DeLuca | R | SI (+0.13) | SI (+0.43) | SI (+0.50) | CH (+0.73) | SI (+1.43) |
| Jorge Mateo | R | SI (+0.12) | SI (+0.22) | SI (+0.45) | CU (+0.81) | CU (+0.89) |
| Junior Caminero | R | SI (+0.34) | SI (+0.48) | SI (+0.78) | CH (+0.26) | SI (+0.94) |
| Liam Hicks | L | SI (+0.46) | SI (+0.33) | SI (+0.83) | SL (+0.65) | SI (+1.10) |
| Nick Fortes | R | SI (+0.71) | SI (+0.91) | SI (+1.65) | CH (+0.66) | SI (+2.95) |
| Richie Palacios | L | SI (+0.54) | SI (+0.32) | SI (+0.72) | SL (+0.82) | SI (+0.37) |
| Ryan Vilade | R | SI (+0.20) | SI (+0.43) | SI (+0.60) | CH (+0.10) | SI (+0.94) |
| Taylor Walls | R | SI (+0.43) | SI (+0.67) | SI (+1.05) | CH (+0.92) | SI (+2.88) |
| Victor Mesa Jr. | L | SI (+0.30) | SI (+0.28) | SI (+0.46) | SL (+0.62) | SI (+0.47) |
| Yandy Díaz | R | SI (+0.30) | SI (+0.80) | SI (+0.83) | SI (+0.73) | SI (+1.97) |

[Count summaries](artifacts/brewers_rays_20261023_staff/pitchers/676879/count_summary.csv) · [Ranked count candidates](artifacts/brewers_rays_20261023_staff/pitchers/676879/count_candidates.csv.gz) · [Exact-history candidate comparisons](artifacts/brewers_rays_20261023_staff/pitchers/676879/history_candidates.csv.gz)

## Abner Uribe (RHP)

Supported arsenal across batting sides: Sinker, Slider. Source-season pitches: 1,032. Last recorded appearance: 2026-10-14; latest four outings: 65 pitches. These records do not establish game availability.

| Rays hitter | Bats | 0–0 opener (ERPA/100) | If opener called strike | If opener ball | 0–2 (ERPA/100) | 3–2 (ERPA/100) |
|---|---|---|---|---|---|---|
| Ben Williamson | R | SL (+0.26) | SL (+0.55) | SL (+0.10) | SL (+0.87) | SL (+1.68) |
| Cedric Mullins | L | SL (+0.23) | SL (+0.86) | SL (+0.18) | SL (+1.30) | SL (+1.54) |
| Chandler Simpson | L | SI (+0.09) | SI (+0.09) | SI (+0.33) | SL (+0.32) | SI (+1.15) |
| Jonathan Aranda | L | SL (+0.28) | SL (+1.04) | SL (+0.33) | SL (+1.48) | SL (+1.88) |
| Jonny DeLuca | R | SL (+0.12) | SL (+0.42) | SI (+0.14) | SL (+0.89) | SL (+0.74) |
| Jorge Mateo | R | SI (+0.10) | SL (+0.34) | SI (+0.43) | SL (+1.24) | SL (+1.48) |
| Junior Caminero | R | SI (+0.14) | SL (+0.05) | SI (+0.29) | SL (+0.50) | SL (+0.28) |
| Liam Hicks | L | SI (+0.02) | SL (+0.05) | SI (+0.21) | SL (+0.49) | SI (+0.52) |
| Nick Fortes | R | SI (+0.04) | SL (+0.38) | SI (+0.31) | SL (+1.00) | SL (+0.77) |
| Richie Palacios | L | SL (+0.21) | SL (+0.60) | SI (+0.02) | SL (+1.28) | SL (+1.56) |
| Ryan Vilade | R | SI (+0.02) | SL (+0.40) | SI (+0.24) | SL (+0.98) | SL (+1.08) |
| Taylor Walls | L | SL (+0.29) | SL (+0.95) | SL (+0.07) | SL (+1.23) | SL (+0.99) |
| Victor Mesa Jr. | L | SL (+0.16) | SL (+0.64) | SI (+0.02) | SL (+1.21) | SL (+1.09) |
| Yandy Díaz | R | SL (+0.02) | SI (+0.09) | SI (+0.37) | SL (+0.20) | SI (+0.64) |

[Count summaries](artifacts/brewers_rays_20261023_staff/pitchers/682842/count_summary.csv) · [Ranked count candidates](artifacts/brewers_rays_20261023_staff/pitchers/682842/count_candidates.csv.gz) · [Exact-history candidate comparisons](artifacts/brewers_rays_20261023_staff/pitchers/682842/history_candidates.csv.gz)

## Antonio Senzatela (RHP)

Supported arsenal across batting sides: Cutter, Four-seam fastball, Sinker. Source-season pitches: 1,190. Last recorded appearance: 2026-10-06; latest four outings: 49 pitches. These records do not establish game availability.

| Rays hitter | Bats | 0–0 opener (ERPA/100) | If opener called strike | If opener ball | 0–2 (ERPA/100) | 3–2 (ERPA/100) |
|---|---|---|---|---|---|---|
| Ben Williamson | R | FF (+0.62) | FF (+0.87) | FF (+0.65) | FC (+0.20) | FF* (+0.00) |
| Cedric Mullins | L | FC (+0.24) | FC (+0.21) | FC (+0.30) | FC (+0.14) | FC (+1.08) |
| Chandler Simpson | L | FF (+0.22) | FF (+0.42) | FF (+0.27) | FF (+0.00) | FF (+0.14) |
| Jonathan Aranda | L | FF (+0.18) | FF (+0.73) | FF (+0.14) | FF (+0.32) | FC (+0.68) |
| Jonny DeLuca | R | FF (+0.40) | FF (+0.79) | FF (+0.32) | FF (+0.02) | FF* (+0.00) |
| Jorge Mateo | R | SI (+0.19) | FF (+0.48) | SI (+0.48) | FF (+0.01) | FF* (+0.00) |
| Junior Caminero | R | FC (+0.05) | FF (+0.18) | SI (+0.14) | FF (+0.13) | FF* (+0.00) |
| Liam Hicks | L | FC (+0.45) | FC (+0.19) | FC (+0.50) | FC (+0.07) | FC (+0.47) |
| Nick Fortes | R | FF (+0.48) | FF (+0.60) | FF (+0.47) | FC (+0.62) | FF* (+0.00) |
| Richie Palacios | L | FF (+0.16) | FF (+0.19) | SI (+0.04) | FF (+0.03) | FC (+0.53) |
| Ryan Vilade | R | FF (+0.09) | FF (+0.69) | SI (+0.16) | FF (+0.38) | FF* (+0.00) |
| Taylor Walls | L | FF (+0.08) | FF (+0.54) | SI (+0.08) | FF (+0.32) | FF (+0.21) |
| Victor Mesa Jr. | L | FF (+0.41) | FF (+0.57) | FF (+0.35) | FF (+0.26) | FF (+0.03) |
| Yandy Díaz | R | FC (+0.39) | FF (+0.26) | FC (+0.38) | FF (+0.42) | FF* (+0.00) |

[Count summaries](artifacts/brewers_rays_20261023_staff/pitchers/622608/count_summary.csv) · [Ranked count candidates](artifacts/brewers_rays_20261023_staff/pitchers/622608/count_candidates.csv.gz) · [Exact-history candidate comparisons](artifacts/brewers_rays_20261023_staff/pitchers/622608/history_candidates.csv.gz)

## Chad Patrick (RHP)

Supported arsenal across batting sides: Cutter, Four-seam fastball, Sinker. Source-season pitches: 1,730. Last recorded appearance: 2026-09-27; latest four outings: 67 pitches. These records do not establish game availability.

| Rays hitter | Bats | 0–0 opener (ERPA/100) | If opener called strike | If opener ball | 0–2 (ERPA/100) | 3–2 (ERPA/100) |
|---|---|---|---|---|---|---|
| Ben Williamson | R | FC (+0.29) | FC (+0.57) | FC (+0.34) | FC (+0.89) | FC (+1.08) |
| Cedric Mullins | L | FC (+0.49) | FC (+0.76) | FC (+0.69) | FC (+0.77) | FC (+1.33) |
| Chandler Simpson | L | FC (+0.39) | FC (+0.56) | FC (+0.33) | FC (+0.55) | SI (+0.90) |
| Jonathan Aranda | L | FC (+0.39) | FC (+0.60) | FC (+0.58) | FC (+0.65) | FC (+1.54) |
| Jonny DeLuca | R | FC (+0.28) | FC (+0.48) | FC (+0.34) | FC (+0.70) | FC (+1.19) |
| Jorge Mateo | R | FC (+0.08) | FC (+0.38) | SI (+0.29) | FC (+0.75) | FC (+0.97) |
| Junior Caminero | R | FC (+0.09) | FC (+0.16) | FC (+0.07) | FF (+0.13) | SI (+1.00) |
| Liam Hicks | L | FC (+0.76) | FC (+0.78) | FC (+0.89) | FC (+0.44) | FC (+0.61) |
| Nick Fortes | R | FC (+0.16) | FC (+0.52) | FC (+0.16) | FC (+1.25) | FC (+1.00) |
| Richie Palacios | L | FC (+0.32) | FC (+0.63) | FC (+0.45) | FC (+0.54) | FC (+0.76) |
| Ryan Vilade | R | FC (+0.16) | FC (+0.35) | FC (+0.14) | FF (+0.32) | FC (+0.46) |
| Taylor Walls | L | FC (+0.21) | FC (+0.38) | FC (+0.30) | FF (+0.19) | SI (+0.83) |
| Victor Mesa Jr. | L | FF (+0.18) | FC (+0.32) | FC (+0.19) | FC (+0.19) | FC (+0.40) |
| Yandy Díaz | R | FC (+0.47) | FC (+0.37) | FC (+0.48) | FF (+0.39) | FC (+0.38) |

[Count summaries](artifacts/brewers_rays_20261023_staff/pitchers/694477/count_summary.csv) · [Ranked count candidates](artifacts/brewers_rays_20261023_staff/pitchers/694477/count_candidates.csv.gz) · [Exact-history candidate comparisons](artifacts/brewers_rays_20261023_staff/pitchers/694477/history_candidates.csv.gz)

## DL Hall (LHP)

Supported arsenal across batting sides: Changeup, Curveball, Sinker, Slider, Sweeper. Source-season pitches: 1,078. Last recorded appearance: 2026-10-14; latest four outings: 81 pitches. These records do not establish game availability.

| Rays hitter | Bats | 0–0 opener (ERPA/100) | If opener called strike | If opener ball | 0–2 (ERPA/100) | 3–2 (ERPA/100) |
|---|---|---|---|---|---|---|
| Ben Williamson | R | SI (+0.43) | CU (+0.57) | SI (+1.20) | CU (+0.28) | CU (+0.84) |
| Cedric Mullins | L | SL (+0.18) | SL (+0.67) | SL (+0.12) | ST* (+0.00) | SI* (+0.00) |
| Chandler Simpson | L | SI (+0.26) | SL (+0.38) | SI (+0.83) | ST* (+0.00) | SI* (+0.00) |
| Jonathan Aranda | L | SI (+0.02) | SL (+0.35) | SI (+0.14) | ST* (+0.00) | SI* (+0.00) |
| Jonny DeLuca | R | CU (+0.34) | CU (+0.80) | CU (+0.58) | CU (+0.12) | CU (+0.60) |
| Jorge Mateo | R | CU (+0.34) | CU (+0.91) | CU (+0.41) | CU (+0.57) | CU (+2.76) |
| Junior Caminero | R | SI (+0.22) | CU (+0.97) | SI (+0.71) | CU (+0.51) | CU (+2.03) |
| Liam Hicks | L | SI (+0.18) | SL (+0.74) | SI (+0.78) | ST* (+0.00) | SI* (+0.00) |
| Nick Fortes | R | SI (+0.71) | CU (+0.44) | SI (+1.97) | CU (+0.12) | SI (+1.00) |
| Richie Palacios | L | SI (+0.40) | SL (+0.44) | SI (+0.99) | ST* (+0.00) | SI* (+0.00) |
| Ryan Vilade | R | CU (+0.26) | CU (+0.87) | SI (+0.61) | CU (+0.46) | CU (+1.51) |
| Taylor Walls | R | SI (+0.26) | CU (+0.46) | SI (+0.99) | CH (+0.18) | SI (+0.71) |
| Victor Mesa Jr. | L | SI (+0.08) | SL (+0.51) | SI (+0.30) | ST* (+0.00) | SI* (+0.00) |
| Yandy Díaz | R | CU (+0.34) | CU (+1.03) | SI (+0.78) | CU (+0.41) | CU (+1.34) |

[Count summaries](artifacts/brewers_rays_20261023_staff/pitchers/669084/count_summary.csv) · [Ranked count candidates](artifacts/brewers_rays_20261023_staff/pitchers/669084/count_candidates.csv.gz) · [Exact-history candidate comparisons](artifacts/brewers_rays_20261023_staff/pitchers/669084/history_candidates.csv.gz)

## Dustin May (RHP)

Supported arsenal across batting sides: Curveball, Cutter, Four-seam fastball, Sinker, Sweeper. Source-season pitches: 2,509. Last recorded appearance: 2026-10-15; latest four outings: 168 pitches. These records do not establish game availability.

| Rays hitter | Bats | 0–0 opener (ERPA/100) | If opener called strike | If opener ball | 0–2 (ERPA/100) | 3–2 (ERPA/100) |
|---|---|---|---|---|---|---|
| Ben Williamson | R | FF (+0.79) | FF (+1.04) | FF (+0.73) | FF (+0.33) | SI (+0.41) |
| Cedric Mullins | L | SI (+0.44) | FF (+0.54) | SI (+0.68) | FF (+0.67) | SI (+0.97) |
| Chandler Simpson | L | FF (+1.00) | FF (+1.67) | SI (+1.19) | FF (+1.33) | SI (+3.42) |
| Jonathan Aranda | L | SI (+0.41) | FF (+0.56) | SI (+0.55) | FF (+0.50) | ST (+0.91) |
| Jonny DeLuca | R | FF (+0.45) | FF (+0.66) | SI (+0.35) | FF (+0.46) | SI (+0.85) |
| Jorge Mateo | R | SI (+0.61) | FF (+0.61) | SI (+0.93) | FF (+0.47) | SI (+0.55) |
| Junior Caminero | R | SI (+0.35) | FF (+0.67) | SI (+0.50) | FF (+0.68) | SI (+1.14) |
| Liam Hicks | L | FC (+0.44) | FF (+0.92) | SI (+0.45) | FF (+1.18) | SI (+3.15) |
| Nick Fortes | R | FF (+0.54) | FF (+0.65) | SI (+0.46) | FF (+0.33) | SI (+1.03) |
| Richie Palacios | L | FF (+0.49) | FF (+0.50) | SI (+0.62) | ST (+0.27) | SI (+1.68) |
| Ryan Vilade | R | SI (+0.27) | FF (+0.72) | SI (+0.51) | FF (+0.88) | SI (+0.66) |
| Taylor Walls | L | SI (+0.53) | FF (+0.80) | SI (+0.95) | FF (+0.85) | SI (+2.03) |
| Victor Mesa Jr. | L | FF (+0.74) | FF (+0.85) | FF (+0.64) | FF (+1.11) | FF (+1.01) |
| Yandy Díaz | R | SI (+0.20) | FF (+0.74) | SI (+0.54) | FF (+1.35) | SI (+1.01) |

[Count summaries](artifacts/brewers_rays_20261023_staff/pitchers/669160/count_summary.csv) · [Ranked count candidates](artifacts/brewers_rays_20261023_staff/pitchers/669160/count_candidates.csv.gz) · [Exact-history candidate comparisons](artifacts/brewers_rays_20261023_staff/pitchers/669160/history_candidates.csv.gz)

## Jacob Misiorowski (RHP)

Supported arsenal across batting sides: Curveball, Cutter, Four-seam fastball, Slider. Source-season pitches: 2,829. Last recorded appearance: 2026-10-11; latest four outings: 294 pitches. These records do not establish game availability.

| Rays hitter | Bats | 0–0 opener (ERPA/100) | If opener called strike | If opener ball | 0–2 (ERPA/100) | 3–2 (ERPA/100) |
|---|---|---|---|---|---|---|
| Ben Williamson | R | FF (+0.20) | FF (+0.24) | FF (+0.14) | CU (+0.50) | SL (+2.23) |
| Cedric Mullins | L | FC (+0.45) | SL (+0.46) | FC (+0.88) | SL (+0.43) | SL (+2.55) |
| Chandler Simpson | L | FF (+0.25) | FF (+0.67) | FF (+0.29) | FF (+0.25) | FC (+0.45) |
| Jonathan Aranda | L | FC (+0.24) | FF (+0.15) | FC (+0.61) | SL (+0.29) | SL (+2.13) |
| Jonny DeLuca | R | FF (+0.05) | FC (+0.13) | FC (+0.43) | SL (+0.38) | CU (+2.02) |
| Jorge Mateo | R | FF (+0.05) | SL (+0.09) | FC (+0.18) | SL (+0.90) | SL (+2.50) |
| Junior Caminero | R | FF (+0.16) | FF (+0.30) | FF (+0.13) | CU (+0.63) | CU (+1.81) |
| Liam Hicks | L | FC (+0.70) | FC (+0.46) | FC (+1.05) | SL (+0.79) | SL (+1.99) |
| Nick Fortes | R | FF (+0.20) | FC (+0.37) | FC (+0.28) | SL (+1.15) | SL (+2.48) |
| Richie Palacios | L | FC (+0.10) | SL (+0.28) | FC (+0.49) | SL (+1.34) | SL (+4.31) |
| Ryan Vilade | R | FC (+0.17) | FF (+0.07) | FC (+0.53) | SL (+0.25) | SL (+1.79) |
| Taylor Walls | L | SL (+0.08) | FF (+0.27) | FC (+0.30) | FF (+0.44) | SL (+1.95) |
| Victor Mesa Jr. | L | FF (+0.10) | FF (+0.10) | FC (+0.17) | FF (+0.14) | SL (+1.11) |
| Yandy Díaz | R | FC (+0.42) | FF (+0.34) | FC (+0.86) | FF (+0.59) | FC (+0.66) |

[Count summaries](artifacts/brewers_rays_20261023_staff/pitchers/694819/count_summary.csv) · [Ranked count candidates](artifacts/brewers_rays_20261023_staff/pitchers/694819/count_candidates.csv.gz) · [Exact-history candidate comparisons](artifacts/brewers_rays_20261023_staff/pitchers/694819/history_candidates.csv.gz)

## JoJo Romero (LHP)

Supported arsenal across batting sides: Changeup, Sinker, Sweeper. Source-season pitches: 1,004. Last recorded appearance: 2026-10-15; latest four outings: 82 pitches. These records do not establish game availability.

| Rays hitter | Bats | 0–0 opener (ERPA/100) | If opener called strike | If opener ball | 0–2 (ERPA/100) | 3–2 (ERPA/100) |
|---|---|---|---|---|---|---|
| Ben Williamson | R | SI (+0.15) | ST (+0.98) | SI (+0.45) | ST (+0.85) | ST (+1.40) |
| Cedric Mullins | L | ST (+0.38) | ST (+0.69) | ST (+0.37) | ST* (+0.00) | ST* (+0.00) |
| Chandler Simpson | L | ST (+0.34) | ST (+1.08) | ST (+0.05) | ST* (+0.00) | ST* (+0.00) |
| Jonathan Aranda | L | ST (+0.40) | ST (+0.83) | ST (+0.43) | ST* (+0.00) | ST* (+0.00) |
| Jonny DeLuca | R | ST (+0.71) | ST (+1.53) | ST (+0.90) | ST (+1.00) | ST (+2.17) |
| Jorge Mateo | R | ST (+0.78) | ST (+1.40) | ST (+0.92) | CH (+0.10) | ST (+0.75) |
| Junior Caminero | R | ST (+0.42) | ST (+1.29) | ST (+0.52) | ST (+0.79) | ST (+1.67) |
| Liam Hicks | L | SI (+0.22) | ST (+0.22) | SI (+0.70) | ST* (+0.00) | ST* (+0.00) |
| Nick Fortes | R | SI (+0.23) | ST (+1.03) | SI (+0.64) | ST (+0.32) | SI (+0.44) |
| Richie Palacios | L | SI (+0.33) | ST (+0.18) | SI (+0.71) | ST* (+0.00) | ST* (+0.00) |
| Ryan Vilade | R | ST (+0.52) | ST (+1.22) | ST (+0.61) | ST (+0.24) | ST (+0.73) |
| Taylor Walls | R | ST (+0.21) | ST (+1.13) | SI (+0.36) | ST (+0.47) | ST (+0.83) |
| Victor Mesa Jr. | L | ST (+0.01) | ST (+0.36) | SI (+0.15) | ST* (+0.00) | ST* (+0.00) |
| Yandy Díaz | R | ST (+0.59) | ST (+1.46) | ST (+0.57) | ST (+0.79) | ST (+1.06) |

[Count summaries](artifacts/brewers_rays_20261023_staff/pitchers/668941/count_summary.csv) · [Ranked count candidates](artifacts/brewers_rays_20261023_staff/pitchers/668941/count_candidates.csv.gz) · [Exact-history candidate comparisons](artifacts/brewers_rays_20261023_staff/pitchers/668941/history_candidates.csv.gz)

## Kyle Harrison (LHP)

Supported arsenal across batting sides: Changeup, Four-seam fastball, Slurve. Source-season pitches: 2,106. Last recorded appearance: 2026-09-26; latest four outings: 113 pitches. These records do not establish game availability.

| Rays hitter | Bats | 0–0 opener (ERPA/100) | If opener called strike | If opener ball | 0–2 (ERPA/100) | 3–2 (ERPA/100) |
|---|---|---|---|---|---|---|
| Ben Williamson | R | FF (+0.38) | SV (+0.29) | FF (+0.77) | SV (+1.10) | SV (+1.06) |
| Cedric Mullins | L | SV (+0.06) | SV (+0.21) | SV (+0.24) | SV (+0.38) | SV (+1.46) |
| Chandler Simpson | L | FF (+0.14) | SV (+0.26) | FF (+0.25) | SV (+0.95) | SV (+1.11) |
| Jonathan Aranda | L | SV (+0.07) | SV (+0.16) | SV (+0.14) | SV (+0.23) | SV (+0.65) |
| Jonny DeLuca | R | FF (+0.26) | SV (+0.21) | FF (+0.43) | SV (+0.36) | SV (+0.52) |
| Jorge Mateo | R | FF (+0.17) | SV (+0.41) | FF (+0.31) | SV (+1.52) | SV (+2.28) |
| Junior Caminero | R | SV (+0.59) | SV (+0.88) | SV (+0.65) | SV (+1.03) | SV (+1.90) |
| Liam Hicks | L | FF (+0.12) | SV (+0.23) | FF (+0.12) | SV (+0.84) | SV (+1.21) |
| Nick Fortes | R | FF (+0.45) | SV (+0.27) | FF (+0.89) | SV (+0.92) | SV (+0.16) |
| Richie Palacios | L | FF (+0.17) | FF (+0.07) | FF (+0.18) | SV (+0.31) | SV (+0.27) |
| Ryan Vilade | R | FF (+0.17) | SV (+0.22) | SV (+0.33) | SV (+0.30) | SV (+0.93) |
| Taylor Walls | R | FF (+0.15) | SV (+0.27) | SV (+0.41) | SV (+0.56) | SV (+1.09) |
| Victor Mesa Jr. | L | FF (+0.07) | SV (+0.06) | FF (+0.03) | SV (+0.13) | SV (+0.50) |
| Yandy Díaz | R | FF (+0.22) | SV (+0.20) | FF (+0.35) | SV (+0.28) | SV (+0.34) |

[Count summaries](artifacts/brewers_rays_20261023_staff/pitchers/690986/count_summary.csv) · [Ranked count candidates](artifacts/brewers_rays_20261023_staff/pitchers/690986/count_candidates.csv.gz) · [Exact-history candidate comparisons](artifacts/brewers_rays_20261023_staff/pitchers/690986/history_candidates.csv.gz)

## Logan Henderson (RHP)

Supported arsenal across batting sides: Changeup, Cutter, Four-seam fastball, Sweeper. Source-season pitches: 1,641. Last recorded appearance: 2026-10-12; latest four outings: 310 pitches. These records do not establish game availability.

| Rays hitter | Bats | 0–0 opener (ERPA/100) | If opener called strike | If opener ball | 0–2 (ERPA/100) | 3–2 (ERPA/100) |
|---|---|---|---|---|---|---|
| Ben Williamson | R | FF (+0.52) | FF (+0.54) | FF (+0.72) | CH (+0.70) | FF (+0.21) |
| Cedric Mullins | L | FC (+0.73) | FC (+0.42) | FC (+1.11) | CH (+0.16) | CH (+0.28) |
| Chandler Simpson | L | FF (+0.52) | FF (+0.43) | FF (+0.83) | CH (+0.67) | CH (+0.29) |
| Jonathan Aranda | L | FC (+0.22) | FF (+0.12) | FC (+0.51) | FF (+0.03) | FF (+0.03) |
| Jonny DeLuca | R | FF (+0.25) | FF (+0.28) | FF (+0.18) | CH (+0.94) | CH (+1.52) |
| Jorge Mateo | R | FF (+0.22) | FF (+0.35) | FC (+0.46) | CH (+0.83) | CH (+0.88) |
| Junior Caminero | R | FF (+0.18) | FF (+0.35) | FF (+0.37) | CH (+0.81) | CH (+0.66) |
| Liam Hicks | L | FC (+0.78) | FF (+0.45) | FC (+1.18) | CH (+0.15) | FF (+0.53) |
| Nick Fortes | R | FF (+0.47) | FF (+0.25) | FF (+0.57) | CH (+1.31) | CH (+1.03) |
| Richie Palacios | L | FF (+0.50) | FF (+0.27) | FC (+0.72) | CH (+0.62) | CH (+0.67) |
| Ryan Vilade | R | FF (+0.16) | FF (+0.34) | FC (+0.50) | CH (+0.47) | CH (+0.17) |
| Taylor Walls | L | FF (+0.15) | FF (+0.16) | FC (+0.26) | CH (+0.38) | CH (+0.82) |
| Victor Mesa Jr. | L | FF (+0.59) | FF (+0.38) | FF (+0.70) | CH (+0.18) | FF (+0.01) |
| Yandy Díaz | R | FC (+0.48) | FF (+0.28) | FC (+1.08) | FF (+0.43) | FF (+0.13) |

[Count summaries](artifacts/brewers_rays_20261023_staff/pitchers/701656/count_summary.csv) · [Ranked count candidates](artifacts/brewers_rays_20261023_staff/pitchers/701656/count_candidates.csv.gz) · [Exact-history candidate comparisons](artifacts/brewers_rays_20261023_staff/pitchers/701656/history_candidates.csv.gz)

## Robert Gasser (LHP)

Supported arsenal across batting sides: Changeup, Cutter, Four-seam fastball, Sinker, Sweeper. Source-season pitches: 1,945. Last recorded appearance: 2026-10-14; latest four outings: 322 pitches. These records do not establish game availability.

| Rays hitter | Bats | 0–0 opener (ERPA/100) | If opener called strike | If opener ball | 0–2 (ERPA/100) | 3–2 (ERPA/100) |
|---|---|---|---|---|---|---|
| Ben Williamson | R | SI (+0.31) | ST (+0.56) | SI (+0.89) | ST (+1.55) | ST (+1.47) |
| Cedric Mullins | L | FC (+0.31) | FC (+0.48) | FC (+0.36) | FF (+0.68) | ST (+0.09) |
| Chandler Simpson | L | FF (+0.21) | ST (+0.63) | SI (+0.37) | ST (+1.74) | ST (+0.43) |
| Jonathan Aranda | L | FC (+0.36) | ST (+0.29) | FC (+0.50) | ST (+0.33) | ST (+0.73) |
| Jonny DeLuca | R | FF (+0.44) | FF (+0.57) | FF (+0.33) | ST (+0.49) | ST (+1.70) |
| Jorge Mateo | R | FC (+0.43) | ST (+0.52) | FC (+0.45) | CH (+0.84) | CH (+1.08) |
| Junior Caminero | R | FC (+0.46) | FF (+0.28) | FC (+0.71) | FF (+0.21) | ST (+1.33) |
| Liam Hicks | L | SI (+0.56) | SI (+0.33) | SI (+1.05) | ST (+0.58) | SI (+1.03) |
| Nick Fortes | R | SI (+0.44) | ST (+0.39) | SI (+1.45) | ST (+0.53) | SI (+1.81) |
| Richie Palacios | L | SI (+0.31) | FF (+0.60) | SI (+0.56) | FF (+0.75) | SI (+0.80) |
| Ryan Vilade | R | FC (+0.26) | FF (+0.35) | FC (+0.48) | FF (+0.51) | FC (+0.78) |
| Taylor Walls | R | SI (+0.13) | ST (+0.32) | SI (+0.63) | ST (+0.26) | SI (+0.57) |
| Victor Mesa Jr. | L | FC (+0.63) | FC (+0.57) | FC (+0.87) | FF (+0.35) | SI (+0.06) |
| Yandy Díaz | R | FC (+0.33) | ST (+0.62) | FC (+0.46) | FF (+0.19) | SI (+1.05) |

[Count summaries](artifacts/brewers_rays_20261023_staff/pitchers/688107/count_summary.csv) · [Ranked count candidates](artifacts/brewers_rays_20261023_staff/pitchers/688107/count_candidates.csv.gz) · [Exact-history candidate comparisons](artifacts/brewers_rays_20261023_staff/pitchers/688107/history_candidates.csv.gz)

## Shane Drohan (LHP)

Supported arsenal across batting sides: Changeup, Curveball, Cutter, Four-seam fastball, Sinker, Slider. Source-season pitches: 2,026. Last recorded appearance: 2026-10-15; latest four outings: 116 pitches. These records do not establish game availability.

| Rays hitter | Bats | 0–0 opener (ERPA/100) | If opener called strike | If opener ball | 0–2 (ERPA/100) | 3–2 (ERPA/100) |
|---|---|---|---|---|---|---|
| Ben Williamson | R | FF (+0.53) | SL (+0.82) | SI (+0.67) | SL (+1.71) | SL (+3.01) |
| Cedric Mullins | L | FC (+0.43) | FC (+0.71) | FC (+0.36) | SL (+0.69) | SL (+1.00) |
| Chandler Simpson | L | FF (+0.68) | FF (+0.62) | FF (+0.88) | SL (+0.99) | SL (+0.31) |
| Jonathan Aranda | L | FC (+0.52) | FC (+0.91) | FC (+0.58) | FF (+1.01) | SI (+0.20) |
| Jonny DeLuca | R | FF (+0.58) | FF (+0.80) | FF (+0.69) | SL (+0.98) | SL (+2.50) |
| Jorge Mateo | R | FC (+0.50) | SL (+0.83) | FC (+0.68) | SL (+1.78) | SL (+2.78) |
| Junior Caminero | R | FC (+0.92) | FC (+1.03) | FC (+1.30) | CH (+0.73) | SL (+1.62) |
| Liam Hicks | L | SI (+0.16) | SL (+0.42) | SI (+1.07) | SL (+0.82) | SL (+0.34) |
| Nick Fortes | R | SL (+0.44) | SL (+1.20) | SI (+1.16) | SL (+1.97) | SL (+3.51) |
| Richie Palacios | L | FF (+0.47) | FF (+0.82) | SI (+0.65) | SL (+0.63) | SL (+0.51) |
| Ryan Vilade | R | SL (+0.54) | SL (+1.00) | FC (+0.79) | SL (+1.08) | SL (+2.52) |
| Taylor Walls | R | FF (+0.29) | FF (+0.66) | FC (+0.43) | CH (+0.77) | SL (+0.98) |
| Victor Mesa Jr. | L | FC (+0.66) | FC (+0.70) | FC (+0.67) | SL (+0.55) | SL (+0.58) |
| Yandy Díaz | R | FC (+0.55) | FC (+0.33) | FC (+0.74) | FF (+0.37) | SI (+0.53) |

[Count summaries](artifacts/brewers_rays_20261023_staff/pitchers/675660/count_summary.csv) · [Ranked count candidates](artifacts/brewers_rays_20261023_staff/pitchers/675660/count_candidates.csv.gz) · [Exact-history candidate comparisons](artifacts/brewers_rays_20261023_staff/pitchers/675660/history_candidates.csv.gz)

## Trevor Megill (RHP)

Supported arsenal across batting sides: Four-seam fastball, Knuckle curve. Source-season pitches: 952. Last recorded appearance: 2026-10-14; latest four outings: 61 pitches. These records do not establish game availability.

| Rays hitter | Bats | 0–0 opener (ERPA/100) | If opener called strike | If opener ball | 0–2 (ERPA/100) | 3–2 (ERPA/100) |
|---|---|---|---|---|---|---|
| Ben Williamson | R | FF (+0.22) | FF (+0.23) | FF (+0.59) | KC (+0.83) | KC (+1.26) |
| Cedric Mullins | L | FF (+0.17) | FF (+0.21) | FF (+0.23) | FF (+0.04) | FF* (+0.00) |
| Chandler Simpson | L | FF (+0.26) | FF (+0.32) | FF (+0.45) | KC (+0.65) | FF* (+0.00) |
| Jonathan Aranda | L | KC (+0.31) | KC (+0.27) | KC (+0.55) | KC (+0.80) | FF* (+0.00) |
| Jonny DeLuca | R | FF (+0.11) | FF (+0.18) | FF (+0.24) | KC (+0.48) | KC (+2.25) |
| Jorge Mateo | R | FF (+0.23) | FF (+0.31) | FF (+0.59) | KC (+0.54) | KC (+1.49) |
| Junior Caminero | R | FF (+0.10) | FF (+0.12) | FF (+0.34) | KC (+0.51) | KC (+1.42) |
| Liam Hicks | L | FF (+0.28) | FF (+0.35) | FF (+0.55) | KC (+0.03) | FF* (+0.00) |
| Nick Fortes | R | FF (+0.33) | FF (+0.34) | FF (+0.80) | KC (+0.85) | KC (+1.43) |
| Richie Palacios | L | FF (+0.10) | KC (+0.04) | FF (+0.09) | KC (+1.10) | FF* (+0.00) |
| Ryan Vilade | R | FF (+0.11) | FF (+0.23) | FF (+0.28) | FF (+0.06) | KC (+0.61) |
| Taylor Walls | L | FF (+0.13) | FF (+0.21) | FF (+0.20) | FF (+0.07) | FF* (+0.00) |
| Victor Mesa Jr. | L | FF (+0.14) | FF (+0.07) | FF (+0.09) | KC (+0.25) | FF* (+0.00) |
| Yandy Díaz | R | FF (+0.20) | FF (+0.38) | FF (+0.48) | FF (+0.16) | KC (+0.62) |

[Count summaries](artifacts/brewers_rays_20261023_staff/pitchers/656730/count_summary.csv) · [Ranked count candidates](artifacts/brewers_rays_20261023_staff/pitchers/656730/count_candidates.csv.gz) · [Exact-history candidate comparisons](artifacts/brewers_rays_20261023_staff/pitchers/656730/history_candidates.csv.gz)
