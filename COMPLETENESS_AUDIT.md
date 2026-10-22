# Repaired completeness audit — October 21, 2026

**Complete for the requested 2026 regular-season cohort.** All 64 previously missing appearances were recovered.

| Check | Result |
|---|---:|
| Pitcher files / verified team participants | 34 / 34 |
| Brewers completed games covered / scheduled | 162 / 162 |
| Brewers physical pitches / MLB logged pitches | 23,650 / 23,650 |
| Missing pitcher appearances | 0 |
| Pitch-count discrepancies | 0 |
| Unexpected pitcher appearances | 0 |
| Raw regular-season event rows, including other-team appearances | 29,439 |

Requested March 1–October 20, 2026; the Brewers regular season ends September 27. Postseason is intentionally outside this cohort. All CSV pitch keys are present and unique; source pitcher identity and requested dates are checked before writing. File hashes bind the audit to the CSVs.

## What caused the gaps

The old `pitcher_id` query was ignored and returned pitches for all pitchers. A controlled April 5–11 query using the old expanded bounds returned exactly 25,000 rows from 411 pitchers, with Grant Anderson’s April 6 game absent. A query using `pitchers_lookup[]`, `type=details`, and the actual inclusive bounds returned 66 Anderson rows and restored that game. Client-side filtering after truncation could not recover omitted rows.

Some apparent count differences were automatic balls or strikes. Statcast includes those events, while MLB physical-pitch counts exclude them. The new audit checks physical rows against `numberOfPitches` and retains automatic events separately. It found no remaining mismatches after the fresh download.

The season pitching-participant endpoint identified Gary Sánchez, Colton Gordon, and Andrew Vaughn as missing from the prior roster. All three are now included. Comparison membership for Kyle Harrison no longer overwrites team membership.

## Verification and resume

The downloader was run twice: the second pass resumed verified checkpoints and reproduced the same raw file hashes while rechecking MLB logs and the team schedule. It uses atomic writes, rejects malformed/error responses, checks truncation limits, and only marks metadata complete after reconciliation passes.

Raw data is preserved, including 95 automatic-event rows across all acquired pitchers and teams. The Brewers subset contains 23,650 physical pitches; 23,619 have the pitch classification and target needed for this first model. The 31 omitted modeling rows remain in raw data.

Original files and the original audit are archived in `data/archive/pre_repair_2026/`. The original snapshot included spring training and exhibition rows; the replacement dataset is regular-season only, so total row counts are not directly comparable.

## Per-pitcher reconciliation

| Pitcher | Saved / expected appearances | Physical pitches / MLB total |
|---|---:|---:|
| Grant Anderson | 52 / 52 | 915 / 915 |
| Aaron Ashby | 75 / 75 | 1582 / 1582 |
| Coleman Crow | 5 / 5 | 295 / 295 |
| Shane Drohan | 33 / 33 | 2001 / 2001 |
| Brian Fitzpatrick | 5 / 5 | 109 / 109 |
| Robert Gasser | 21 / 21 | 1817 / 1817 |
| DL Hall | 47 / 47 | 997 / 997 |
| Kyle Harrison | 28 / 28 | 2106 / 2106 |
| Logan Henderson | 18 / 18 | 1505 / 1505 |
| Jared Koenig | 9 / 9 | 161 / 161 |
| Joel Kuhnel | 45 / 45 | 748 / 748 |
| Dustin May | 31 / 31 | 2399 / 2399 |
| Lance McCullers Jr. | 10 / 10 | 793 / 793 |
| Easton McGee | 9 / 9 | 184 / 184 |
| Trevor Megill | 63 / 63 | 874 / 874 |
| Jacob Misiorowski | 30 / 30 | 2647 / 2647 |
| Thomas Pannone | 1 / 1 | 56 / 56 |
| Chad Patrick | 57 / 57 | 1730 / 1730 |
| Lyon Richardson | 3 / 3 | 68 / 68 |
| Carlos Rodriguez | 4 / 4 | 182 / 182 |
| Drew Rom | 18 / 18 | 300 / 300 |
| JoJo Romero | 55 / 55 | 922 / 922 |
| Antonio Senzatela | 57 / 57 | 1165 / 1165 |
| Brandon Sproat | 22 / 22 | 1754 / 1754 |
| Garrett Stallings | 6 / 6 | 194 / 194 |
| Abner Uribe | 61 / 61 | 918 / 918 |
| Bryse Wilson | 16 / 16 | 558 / 558 |
| Jake Woodford | 19 / 19 | 485 / 485 |
| Brandon Woodruff | 9 / 9 | 639 / 639 |
| Craig Yoho | 34 / 34 | 635 / 635 |
| Angel Zerpa | 12 / 12 | 216 / 216 |
| Gary Sánchez | 2 / 2 | 33 / 33 |
| Colton Gordon | 5 / 5 | 272 / 272 |
| Andrew Vaughn | 2 / 2 | 84 / 84 |

Machine-readable details and exact MLB source URLs: [data/processed/completeness_audit_2026.json](data/processed/completeness_audit_2026.json). Coverage includes all teams’ appearances by the participant list; modeling selects pitches actually thrown for Milwaukee.
