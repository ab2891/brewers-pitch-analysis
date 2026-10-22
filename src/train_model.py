"""Exploratory pre-pitch run-expectancy regression with chronological evaluation."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
import xgboost
from sklearn.compose import ColumnTransformer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import OneHotEncoder
from xgboost import XGBRegressor
from history import HISTORY_NUMERIC, add_history
from model_policy import scoring_model

ROOT = Path(__file__).resolve().parents[1]
KEY = ["game_pk", "at_bat_number", "pitch_number"]
CATEGORICAL = [
    "pitcher", "pitch_type", "stand", "p_throws", "inning_topbot",
    "previous_pitch_type", "previous_description",
]
NUMERIC = [
    "balls", "strikes", "outs_when_up", "inning", "pitch_number",
    "score_diff", "runner_1b", "runner_2b", "runner_3b",
]
FEATURES = CATEGORICAL + NUMERIC
TARGET = "delta_run_exp"
CONTEXT = ["balls", "strikes", "pitch_type", "stand"]


def normalize_columns(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    # The old downloader wrote Savant's BOM as part of a quoted column name.
    frame.columns = [str(c).lstrip("\ufeff").strip('"') for c in frame.columns]
    if frame.columns.duplicated().any():
        raise ValueError("Duplicate columns after normalizing CSV headers")
    return frame


def load_data(raw: Path, audit_path: Path, allow_incomplete: bool, cohort: str):
    if not audit_path.exists():
        raise ValueError("A completeness audit is required before training")
    audit = json.loads(audit_path.read_text())
    if audit.get("status") == "in_progress":
        raise ValueError("Acquisition is still in progress; do not train a partial snapshot")
    if audit.get("status") == "incomplete" and not allow_incomplete:
        raise ValueError("Acquisition audit is incomplete")
    requested = audit["requested"]
    frames, sources, excluded = [], [], set()
    for item in audit["pitchers"]:
        check = item.get("regular_season_reconciliation")
        if check is None:
            raise ValueError(f"Missing reconciliation for {item['name']}")
        for game in check["pitch_count_differences"]:
            excluded.add((str(item["player_id"]), str(game["game_pk"])))
        if check["missing_games"] and not allow_incomplete:
            raise ValueError("Known coverage gaps: use --allow-incomplete for an exploratory run")
        if check["pitch_count_differences"] and not allow_incomplete:
            raise ValueError("Unresolved pitch-count discrepancies require --allow-incomplete")
        if check.get("unexpected_games"):
            raise ValueError("Unreconciled unexpected games in the audit")
        path = raw / f"pitcher_{item['player_id']}_{requested['season']}.csv"
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if item.get("sha256") and item["sha256"] != digest:
            raise ValueError(f"{path.name}: data changed since the audit")
        frame = normalize_columns(pd.read_csv(path, dtype={"pitcher": str, "game_pk": str}))
        needed = set(KEY + [TARGET, "pitch_type", "pitcher", "game_type", "game_date",
            "stand", "p_throws", "inning_topbot", "description", "bat_score", "fld_score",
            "home_team", "away_team", "on_1b", "on_2b", "on_3b", "balls", "strikes",
            "outs_when_up", "inning"])
        if needed - set(frame):
            raise ValueError(f"{path.name}: missing columns {sorted(needed - set(frame))}")
        if not frame["pitcher"].eq(str(item["player_id"])).all():
            raise ValueError(f"{path.name}: contains another pitcher's data")
        sources.append({"file": path.name, "sha256": digest})
        frames.append(frame)
    data = pd.concat(frames, ignore_index=True)
    raw_rows = len(data)
    for col in KEY[1:]:
        data[col] = pd.to_numeric(data[col], errors="coerce")
    if data[KEY].isna().any().any() or data.duplicated(KEY).any():
        raise ValueError("Missing or duplicate pitch keys in source files")
    data["game_date"] = pd.to_datetime(data["game_date"], errors="raise").dt.normalize()
    in_range = data["game_date"].between(pd.Timestamp(requested["start"]), pd.Timestamp(requested["end"]))
    if not in_range.all():
        raise ValueError("Source rows fall outside the audited date range")
    data = data.loc[data["game_type"].eq("R")].copy()
    regular_rows = len(data)
    data["pitching_team"] = np.where(data["inning_topbot"].eq("Top"), data["home_team"], data["away_team"])
    if cohort == "brewers":
        data = data.loc[data["pitching_team"].eq("MIL")].copy()
    cohort_rows = len(data)
    bad_game = pd.Series([(p, g) in excluded for p, g in zip(data["pitcher"], data["game_pk"])], index=data.index)
    data = data.loc[~bad_game].copy()
    data[TARGET] = pd.to_numeric(data[TARGET], errors="coerce")
    missing_target = ~np.isfinite(data[TARGET])
    missing_pitch = data["pitch_type"].isna() | data["pitch_type"].eq("")
    dropped = int((missing_target | missing_pitch).sum())
    data = data.loc[~(missing_target | missing_pitch)].copy()
    if data.empty:
        raise ValueError("No usable pitches after quality filters")
    data = data.sort_values(["game_date"] + KEY).reset_index(drop=True)
    info = {
        "raw_rows": raw_rows, "regular_season_rows": regular_rows,
        "cohort_rows_before_quality_filter": cohort_rows,
        "excluded_discrepant_pitcher_game_rows": int(bad_game.sum()),
        "excluded_missing_target_or_pitch_type": dropped, "usable_rows": len(data),
        "cohort": cohort, "requested": requested, "sources": sources,
        "audit_sha256": hashlib.sha256(audit_path.read_bytes()).hexdigest(),
        "exploratory_incomplete_data": allow_incomplete,
    }
    return data, info


def make_features(data: pd.DataFrame) -> pd.DataFrame:
    result = data.copy()
    for col in ("bat_score", "fld_score", "pitch_number", "balls", "strikes", "outs_when_up", "inning"):
        result[col] = pd.to_numeric(result[col], errors="coerce")
    result["score_diff"] = result["bat_score"] - result["fld_score"]
    for base in ("1b", "2b", "3b"):
        result[f"runner_{base}"] = result[f"on_{base}"].notna().astype(int)
    ordered = result.sort_values(KEY)
    groups = ordered.groupby(["game_pk", "at_bat_number", "pitcher"], sort=False)
    consecutive = ordered["pitch_number"].sub(groups["pitch_number"].shift()).eq(1)
    for source, destination in (("pitch_type", "previous_pitch_type"), ("description", "previous_description")):
        previous = groups[source].shift().where(consecutive, "NO_OBSERVED_PREVIOUS_PITCH")
        result[destination] = previous.reindex(result.index)
    for col in CATEGORICAL:
        result[col] = result[col].fillna("UNKNOWN").astype(str)
    return result


def split_dates(data: pd.DataFrame, validation_start=None, test_start=None):
    dates = sorted(data["game_date"].unique())
    if len(dates) < 15:
        raise ValueError("At least 15 distinct game dates required for chronological evaluation")
    if bool(validation_start) != bool(test_start):
        raise ValueError("Provide both validation and test start dates")
    val_start = pd.Timestamp(validation_start or dates[int(len(dates) * .7)])
    test_start = pd.Timestamp(test_start or dates[int(len(dates) * .85)])
    if val_start >= test_start:
        raise ValueError("Validation must start before test")
    parts = (
        data.loc[data["game_date"] < val_start].copy(),
        data.loc[data["game_date"].between(val_start, test_start, inclusive="left")].copy(),
        data.loc[data["game_date"] >= test_start].copy(),
    )
    games = [set(part["game_pk"]) for part in parts]
    if any(games[i] & games[j] for i in range(3) for j in range(i + 1, 3)):
        raise ValueError("A game spans splits; reconcile dates before training")
    if min(map(len, parts)) < 100:
        raise ValueError("Each chronological split must contain at least 100 pitches")
    return parts


def metrics(y, predictions):
    return {"rmse": float(np.sqrt(mean_squared_error(y, predictions))),
            "mae": float(mean_absolute_error(y, predictions)), "r2": float(r2_score(y, predictions))}


def context_predictions(train, other):
    global_mean = float(train[TARGET].mean())
    grouped = train.groupby(CONTEXT, dropna=False)[TARGET].agg(["sum", "count"])
    grouped["estimate"] = (grouped["sum"] + 20 * global_mean) / (grouped["count"] + 20)
    return other[CONTEXT].merge(grouped[["estimate"]], how="left", on=CONTEXT, sort=False)["estimate"].fillna(global_mean).to_numpy()


def bootstrap_improvement(test, baseline, predictions):
    """Paired game bootstrap: positive RMSE difference favors XGBoost."""
    errors = pd.DataFrame({"game_pk": test["game_pk"].to_numpy(),
        "baseline": (test[TARGET].to_numpy() - baseline) ** 2,
        "xgboost": (test[TARGET].to_numpy() - predictions) ** 2, "n": 1})
    sums = errors.groupby("game_pk")[["baseline", "xgboost", "n"]].sum().to_numpy()
    rng = np.random.default_rng(42)
    sampled = sums[rng.integers(0, len(sums), size=(1000, len(sums)))].sum(axis=1)
    deltas = np.sqrt(sampled[:, 0] / sampled[:, 2]) - np.sqrt(sampled[:, 1] / sampled[:, 2])
    return {"unit": "whole game", "resamples": 1000,
        "rmse_improvement_95_percent_interval": np.quantile(deltas, [.025, .975]).tolist()}


def candidate_estimates(train, test, encoder, model, minimum, features=FEATURES):
    # Repertoire and support use training data only. Alternatives are associations,
    # not counterfactual effects or validated recommendations.
    support = train.groupby(["pitcher", "pitch_type", "stand"]).size().rename("training_support").reset_index()
    support = support.loc[support["training_support"] >= minimum]
    candidates = test.drop(columns=["pitch_type"]).merge(support, on=["pitcher", "stand"], how="inner")
    if candidates.empty:
        return pd.DataFrame()
    candidates["estimated_batting_run_delta"] = model.predict(encoder.transform(candidates[features]))
    candidates["estimated_rank"] = candidates.groupby(KEY)["estimated_batting_run_delta"].rank(method="min")
    return candidates[KEY + ["pitcher", "game_date", "stand", "pitch_type", "training_support",
                            "estimated_batting_run_delta", "estimated_rank"]]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, default=ROOT / "data/raw")
    parser.add_argument("--audit", type=Path, default=ROOT / "data/processed/completeness_audit_2026.json")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--allow-incomplete", action="store_true", help="Allow exploratory training after excluding known discrepant pitcher-games")
    parser.add_argument("--cohort", choices=["brewers", "all-roster"], default="brewers")
    parser.add_argument("--min-support", type=int, default=50)
    parser.add_argument("--feature-set", choices=["base", "history"], default="history")
    parser.add_argument("--validation-start", default="2026-08-02")
    parser.add_argument("--test-start", default="2026-09-22")
    args = parser.parse_args()
    if args.min_support < 1:
        parser.error("--min-support must be positive")
    data, info = load_data(args.raw, args.audit, args.allow_incomplete, args.cohort)
    data = make_features(data)
    if args.feature_set == "history":
        data = add_history(data)
    numeric = NUMERIC + (HISTORY_NUMERIC if args.feature_set == "history" else [])
    features = CATEGORICAL + numeric
    train, validation, test = split_dates(data, args.validation_start, args.test_start)
    encoder = ColumnTransformer([
        ("categorical", OneHotEncoder(handle_unknown="ignore", sparse_output=False, dtype=np.float32), CATEGORICAL),
        ("numeric", "passthrough", numeric),
    ])
    x_train = encoder.fit_transform(train[features])
    x_validation = encoder.transform(validation[features])
    candidates_trained = []
    for depth, child, regularization in [(2, 50, 20), (3, 50, 20), (4, 100, 30)]:
        fitted = XGBRegressor(objective="reg:squarederror", n_estimators=1000, learning_rate=.03,
            max_depth=depth, min_child_weight=child, subsample=.8, colsample_bytree=.8,
            reg_lambda=regularization, tree_method="hist", n_jobs=4, random_state=42,
            early_stopping_rounds=50, eval_metric="rmse")
        fitted.fit(x_train, train[TARGET], eval_set=[(x_validation, validation[TARGET])], verbose=False)
        score = metrics(validation[TARGET], fitted.predict(x_validation))["rmse"]
        candidates_trained.append((score, fitted))
    _, model = min(candidates_trained, key=lambda pair: pair[0])
    output = args.output or ROOT / "artifacts" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    output.mkdir(parents=True, exist_ok=False)
    selection = {"recorded_before_test_scoring": datetime.now(timezone.utc).isoformat(),
        "validation_start": args.validation_start, "test_start": args.test_start,
        "candidates": [{"validation_rmse": score, "max_depth": m.max_depth,
                        "min_child_weight": m.min_child_weight, "best_iteration": m.best_iteration}
                       for score, m in candidates_trained], "selected_depth": model.max_depth}
    (output / "selection.json").write_text(json.dumps(selection, indent=2) + "\n")
    evaluation, predictions = {}, {}
    for name, part in (("validation", validation), ("test", test)):
        pred = {
            "training_mean": np.full(len(part), train[TARGET].mean()),
            "shrunk_context_mean": context_predictions(train, part),
            "xgboost": model.predict(encoder.transform(part[features])),
        }
        evaluation[name] = {method: metrics(part[TARGET], values) for method, values in pred.items()}
        predictions[name] = pred
    # Choose using validation only; test metrics are reported without further tuning.
    selected = min(evaluation["validation"], key=lambda name: evaluation["validation"][name]["rmse"])
    baseline = min(("training_mean", "shrunk_context_mean"), key=lambda name: evaluation["validation"][name]["rmse"])
    uncertainty = bootstrap_improvement(test, predictions["test"][baseline], predictions["test"]["xgboost"])
    uncertainty["baseline_selected_on_validation"] = baseline
    deployed = scoring_model(evaluation, selected, uncertainty["rmse_improvement_95_percent_interval"], "rmse")
    joblib.dump(encoder, output / "encoder.joblib")
    (output / "audit.json").write_bytes(args.audit.read_bytes())
    model.save_model(output / "xgboost.ubj")
    test[list(dict.fromkeys(KEY + ["game_date"] + features))].to_csv(output / "test_contexts.csv", index=False)
    context = train.groupby(CONTEXT, dropna=False)[TARGET].agg(["sum", "count"]).reset_index()
    context.to_csv(output / "context_baseline.csv", index=False)
    for name, part in (("validation", validation), ("test", test)):
        result = part[KEY + ["game_date", "pitcher", "pitch_type", "pitching_team", TARGET]].copy()
        for method, values in predictions[name].items():
            result[f"predicted_{method}"] = values
        result.to_csv(output / f"{name}_predictions.csv", index=False)
    by_pitcher = []
    for pitcher, indices in test.groupby("pitcher").indices.items():
        group = test.iloc[indices]
        by_pitcher.append({"pitcher": pitcher, "rows": len(group),
            "seen_in_training": pitcher in set(train["pitcher"]),
            **metrics(group[TARGET], predictions["test"]["xgboost"][indices])})
    pd.DataFrame(by_pitcher).to_csv(output / "test_metrics_by_pitcher.csv", index=False)
    importance = pd.DataFrame({"feature": encoder.get_feature_names_out(), "importance": model.feature_importances_})
    importance.sort_values("importance", ascending=False).to_csv(output / "feature_importance.csv", index=False)
    # Only expose alternative estimates if XGBoost earns validation preference.
    candidates = candidate_estimates(train, test, encoder, model, args.min_support, features) if deployed == "xgboost" else pd.DataFrame()
    if not candidates.empty:
        candidates.to_csv(output / "exploratory_pitch_estimates.csv", index=False)
    report = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "target": TARGET, "target_interpretation": "Batting-side change in run expectancy; lower favors pitcher",
        "status": "preliminary six-game evaluation; pitch estimates are observational associations",
        "features": features, "feature_set": args.feature_set, "data": info, "metrics": evaluation,
        "selected_on_validation": selected, "training_target_mean": float(train[TARGET].mean()),
        "scoring_model": deployed,
        "best_iteration": model.best_iteration,
        "parameters": {key: None if isinstance(value, float) and not np.isfinite(value) else value
                       for key, value in model.get_params().items()},
        "test_uncertainty": uncertainty,
        "minimum_repertoire_support": args.min_support, "candidate_estimate_rows": len(candidates),
        "splits": {name: {"rows": len(part), "games": part["game_pk"].nunique(),
            "start": part["game_date"].min().date().isoformat(), "end": part["game_date"].max().date().isoformat()}
            for name, part in (("train", train), ("validation", validation), ("test", test))},
        "versions": {"python": platform.python_version(), "pandas": pd.__version__,
            "numpy": np.__version__, "scikit_learn": sklearn.__version__, "xgboost": xgboost.__version__},
    }
    (output / "metrics.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    lines = ["# Exploratory XGBoost baseline", "", report["status"], "",
        f"Usable pitches: {len(data):,}; cohort: {args.cohort}. Target: `{TARGET}` (lower favors pitcher).",
        "", "| Split | Rows | Dates |", "|---|---:|---|"]
    for name, split in report["splits"].items():
        lines.append(f"| {name} | {split['rows']:,} | {split['start']} through {split['end']} |")
    lines += ["", "| Model | Validation RMSE | Test RMSE | Test MAE |", "|---|---:|---:|---:|"]
    for method in evaluation["test"]:
        v, t = evaluation["validation"][method], evaluation["test"][method]
        lines.append(f"| {method} | {v['rmse']:.5f} | {t['rmse']:.5f} | {t['mae']:.5f} |")
    low, high = uncertainty["rmse_improvement_95_percent_interval"]
    lines += ["", f"Selected on validation RMSE: **{selected}**. XGBoost best iteration: {model.best_iteration}.", "",
        f"Scoring model after the held-out acceptance gate: **{deployed}**.", "",
        f"Test RMSE improvement over {baseline}, 95% paired game-bootstrap interval: "
        f"[{low:.5f}, {high:.5f}]. Positive values favor XGBoost. "
        "This interval measures variation in the observed games, not bias from missing data.", "",
        f"Incomplete-data override: {args.allow_incomplete}. Splits keep whole dates and games together. "
        "The encoder and repertoire support use training data only. Previous pitch features require "
        "a consecutive observed pitch from the same pitcher and plate appearance. "
        "History summaries use strictly earlier calendar dates, including earlier evaluation dates, "
        "as in sequential daily prediction; they use only the acquired pitcher cohort.", "",
        "Inputs exclude current-pitch location, velocity, release, movement, and outcomes. "
        "The pitch type is the candidate action. Pitch classification is recorded retrospectively; "
        "unobserved intent, opponent quality, execution, and selection effects limit interpretation.", "",
        "Alternative estimates, if emitted, are restricted to training-supported pitcher/pitch/handedness "
        "combinations. Their ranks do not establish causal benefit or an optimal pitch. No alternatives "
        "are emitted unless XGBoost wins validation, beats both baselines on test, "
        "and has a positive lower bound on the test improvement interval.", "",
        "See metrics.json for file hashes, versions, filtering counts, features, and model settings. "
        "encoder.joblib and xgboost.ubj preserve the fitted model; context_baseline.csv preserves baseline counts."]
    (output / "REPORT.md").write_text("\n".join(lines) + "\n")
    print(json.dumps({"output": str(output), "selected_on_validation": selected, "metrics": evaluation}, indent=2))


if __name__ == "__main__":
    main()
