"""Prior-calendar-date summaries; no same-day or future labels enter features."""
import numpy as np
import pandas as pd

WHIFFS = {"swinging_strike", "swinging_strike_blocked", "missed_bunt", "swinging_pitchout"}
HISTORY_NUMERIC = [f"{entity}_prior_{stat}" for entity in ("pitcher", "batter")
                   for stat in ("pitches", "run_delta", "whiff_rate")]
MEASUREMENTS = ["release_speed", "release_spin_rate", "release_extension", "release_pos_x", "release_pos_z"]
HISTORY_NUMERIC += [f"pitcher_prior_{name}" for name in MEASUREMENTS]


def add_history(frame):
    result = frame.copy()
    for entity in ("pitcher", "batter"):
        temp = frame[[entity, "game_date"]].copy()
        temp["pitches"] = 1
        temp["run_delta"] = pd.to_numeric(frame["delta_run_exp"], errors="raise")
        temp["whiffs"] = frame["description"].isin(WHIFFS).astype(int)
        aggregate = {"pitches": "sum", "run_delta": "sum", "whiffs": "sum"}
        if entity == "pitcher":
            for name in MEASUREMENTS:
                value = pd.to_numeric(frame[name], errors="coerce")
                temp[name + "_sum"] = value.fillna(0)
                temp[name + "_count"] = value.notna().astype(int)
                aggregate[name + "_sum"] = "sum"
                aggregate[name + "_count"] = "sum"
        daily = temp.groupby([entity, "game_date"], dropna=False).agg(aggregate).reset_index()
        daily = daily.sort_values([entity, "game_date"])
        columns = list(aggregate)
        prior = daily.groupby(entity, dropna=False)[columns].cumsum() - daily[columns]
        daily[f"{entity}_prior_pitches"] = prior["pitches"]
        # Fixed conservative priors avoid learning smoothing constants from test data.
        daily[f"{entity}_prior_run_delta"] = prior["run_delta"] / (prior["pitches"] + 100)
        daily[f"{entity}_prior_whiff_rate"] = (prior["whiffs"] + 10) / (prior["pitches"] + 100)
        names = [f"{entity}_prior_{x}" for x in ("pitches", "run_delta", "whiff_rate")]
        if entity == "pitcher":
            for name in MEASUREMENTS:
                destination = f"pitcher_prior_{name}"
                daily[destination] = prior[name + "_sum"] / prior[name + "_count"].replace(0, np.nan)
                names.append(destination)
        merged = frame[[entity, "game_date"]].merge(daily[[entity, "game_date"] + names],
            on=[entity, "game_date"], how="left", sort=False)
        for name in names:
            result[name] = merged[name].to_numpy()
    return result
