"""Auxiliary whiff-per-pitch classifier; not a run-value recommendation model."""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.metrics import brier_score_loss, log_loss, roc_auc_score
from sklearn.preprocessing import OneHotEncoder
from xgboost import XGBClassifier

from history import HISTORY_NUMERIC, WHIFFS, add_history
from model_policy import scoring_model
from train_model import (CATEGORICAL, CONTEXT, KEY, NUMERIC, ROOT, load_data,
                         make_features, split_dates)


def probability_metrics(y, probability):
    return {"log_loss": float(log_loss(y, probability, labels=[0, 1])),
        "brier_score": float(brier_score_loss(y, probability)),
        "roc_auc": float(roc_auc_score(y, probability)) if len(set(y)) == 2 else None}


def context_baseline(train, other):
    mean = float(train["whiff"].mean())
    table = train.groupby(CONTEXT)["whiff"].agg(["sum", "count"]).reset_index()
    table["estimate"] = (table["sum"] + 20 * mean) / (table["count"] + 20)
    return other[CONTEXT].merge(table[CONTEXT + ["estimate"]], on=CONTEXT,
        how="left", sort=False)["estimate"].fillna(mean).to_numpy(), table


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--validation-start", default="2026-08-02")
    parser.add_argument("--test-start", default="2026-09-22")
    args = parser.parse_args()
    data, info = load_data(ROOT / "data/raw", ROOT / "data/processed/completeness_audit_2026.json", False, "brewers")
    data = add_history(make_features(data))
    data["whiff"] = data["description"].isin(WHIFFS).astype(int)
    train, validation, test = split_dates(data, args.validation_start, args.test_start)
    features = CATEGORICAL + NUMERIC + HISTORY_NUMERIC
    encoder = ColumnTransformer([
        ("categorical", OneHotEncoder(handle_unknown="ignore", sparse_output=False, dtype=np.float32), CATEGORICAL),
        ("numeric", "passthrough", NUMERIC + HISTORY_NUMERIC)])
    x_train = encoder.fit_transform(train[features])
    x_validation = encoder.transform(validation[features])
    fitted = []
    for depth, child, regularization in [(2, 50, 20), (3, 50, 20), (4, 100, 30)]:
        model = XGBClassifier(n_estimators=1000, learning_rate=.03,
            max_depth=depth, min_child_weight=child, reg_lambda=regularization,
            subsample=.8, colsample_bytree=.8, tree_method="hist", n_jobs=4,
            random_state=42, early_stopping_rounds=50, eval_metric="logloss")
        model.fit(x_train, train.whiff, eval_set=[(x_validation, validation.whiff)], verbose=False)
        fitted.append((log_loss(validation.whiff, model.predict_proba(x_validation)[:, 1]), model))
    _, model = min(fitted, key=lambda pair: pair[0])
    frequency = float(train.whiff.mean())
    val_context, table = context_baseline(train, validation)
    validation_predictions = {"training_mean": np.full(len(validation), frequency),
        "shrunk_context_mean": val_context, "xgboost": model.predict_proba(x_validation)[:, 1]}
    validation_metrics = {name: probability_metrics(validation.whiff, p) for name, p in validation_predictions.items()}
    selected = min(validation_metrics, key=lambda name: validation_metrics[name]["log_loss"])
    baseline = min(("training_mean", "shrunk_context_mean"), key=lambda name: validation_metrics[name]["log_loss"])
    output = args.output or ROOT / "artifacts" / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + "_whiff")
    output.mkdir(parents=True, exist_ok=False)
    selection = {"recorded_before_test_scoring": datetime.now(timezone.utc).isoformat(),
        "selected_on_validation": selected, "selected_depth": model.max_depth,
        "candidates": [{"validation_log_loss": float(score), "depth": m.max_depth,
            "min_child_weight": m.min_child_weight, "best_iteration": m.best_iteration} for score, m in fitted]}
    (output / "selection.json").write_text(json.dumps(selection, indent=2) + "\n")
    test_context, _ = context_baseline(train, test)
    predictions = {"training_mean": np.full(len(test), frequency), "shrunk_context_mean": test_context,
        "xgboost": model.predict_proba(encoder.transform(test[features]))[:, 1]}
    test_metrics = {name: probability_metrics(test.whiff, p) for name, p in predictions.items()}
    losses = {}
    y = test.whiff.to_numpy()
    for name in (baseline, "xgboost"):
        p = np.clip(predictions[name], 1e-7, 1 - 1e-7)
        losses[name] = -(y * np.log(p) + (1 - y) * np.log(1 - p))
    errors = pd.DataFrame({"game_pk": test.game_pk.to_numpy(),
        "improvement": losses[baseline] - losses["xgboost"], "n": 1})
    sums = errors.groupby("game_pk")[["improvement", "n"]].sum().to_numpy()
    rng = np.random.default_rng(42)
    samples = sums[rng.integers(0, len(sums), size=(1000, len(sums)))].sum(axis=1)
    interval = np.quantile(samples[:, 0] / samples[:, 1], [.025, .975]).tolist()
    evaluation = {"validation": validation_metrics, "test": test_metrics}
    deployed = scoring_model(evaluation, selected, interval, "log_loss")
    result = test[KEY + ["game_date", "pitcher", "pitch_type", "whiff"]].copy()
    for name, p in predictions.items():
        result[f"predicted_{name}"] = p
    result.to_csv(output / "test_predictions.csv", index=False)
    test[list(dict.fromkeys(KEY + ["game_date"] + features))].to_csv(output / "test_contexts.csv", index=False)
    # Reliability bins are descriptive test diagnostics, never a fitted calibrator.
    result["bin"] = pd.cut(predictions["xgboost"], bins=np.linspace(0, 1, 11), include_lowest=True)
    result.groupby("bin", observed=True).agg(n=("whiff", "size"),
        observed_whiff_rate=("whiff", "mean"), predicted_whiff_rate=("predicted_xgboost", "mean")).to_csv(output / "reliability.csv")
    joblib.dump(encoder, output / "encoder.joblib")
    (output / "audit.json").write_bytes((ROOT / "data/processed/completeness_audit_2026.json").read_bytes())
    model.save_model(output / "xgboost.ubj")
    table.drop(columns="estimate").to_csv(output / "context_baseline.csv", index=False)
    report = {"task": "whiff", "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "target": "whiff per pitch, not conditional on swing", "positive_descriptions": sorted(WHIFFS),
        "status": "auxiliary outcome; preliminary six-game test; not an optimal-pitch model",
        "features": features, "data": info, "selected_on_validation": selected,
        "scoring_model": deployed,
        "training_target_mean": frequency, "best_iteration": model.best_iteration,
        "metrics": {"validation": validation_metrics, "test": test_metrics},
        "test_uncertainty": {"baseline_selected_on_validation": baseline, "unit": "whole game",
            "resamples": 1000, "log_loss_improvement_95_percent_interval": interval},
        "parameters": {k: None if isinstance(v, float) and not np.isfinite(v) else v for k, v in model.get_params().items()},
        "splits": {name: {"rows": len(part), "games": part.game_pk.nunique(),
            "start": part.game_date.min().date().isoformat(), "end": part.game_date.max().date().isoformat()}
            for name, part in (("train", train), ("validation", validation), ("test", test))}}
    (output / "metrics.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    lines = ["# Auxiliary whiff model", "", report["status"], "",
        "| Model | Validation log loss | Test log loss | Test Brier score | Test ROC AUC |",
        "|---|---:|---:|---:|---:|"]
    for name, value in test_metrics.items():
        lines.append(f"| {name} | {validation_metrics[name]['log_loss']:.5f} | {value['log_loss']:.5f} | {value['brier_score']:.5f} | {value['roc_auc']:.5f} |")
    lines += ["", f"Selected on validation: {selected}. Best iteration: {model.best_iteration}.", "",
        f"Scoring model after the held-out acceptance gate: {deployed}.", "",
        f"95% paired-game interval for log-loss improvement over {baseline}: [{interval[0]:.5f}, {interval[1]:.5f}]. Positive favors XGBoost.", "",
        "Training and repertoire history use earlier observed data only. History is updated using "
        "strictly earlier dates, including earlier test dates. Current pitch measurements and outcomes "
        "are excluded. Whiff likelihood alone does not establish run prevention or optimal pitch choice."]
    (output / "REPORT.md").write_text("\n".join(lines) + "\n")
    print(json.dumps({"output": str(output), "selected_on_validation": selected, "metrics": report["metrics"]}, indent=2))


if __name__ == "__main__":
    main()
