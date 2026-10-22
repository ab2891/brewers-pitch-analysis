"""A test-set acceptance gate, separate from validation-based model selection."""


def scoring_model(metrics, selected, interval, loss):
    baselines = ("training_mean", "shrunk_context_mean")
    baseline = min(baselines, key=lambda name: metrics["validation"][name][loss])
    improves_both = all(metrics["test"]["xgboost"][loss] < metrics["test"][name][loss]
                        for name in baselines)
    accepted = selected == "xgboost" and improves_both and interval[0] > 0
    return "xgboost" if accepted else baseline
