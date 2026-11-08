from experiments.timdr_benchmark import run


def test_benchmark_uses_disjoint_calibration_and_holdout_and_reports_metrics():
    result = run()
    assert result["status"] == "synthetic_exploratory_only"
    assert result["calibration_seeds"] == [1000, 1099]
    assert result["holdout_seeds"] == [9000, 9099]
    # 100 holdout seeds × 16 windows per seed = 1,600 windows.
    assert result["holdout_windows"] == 1600
    for name in ("simple_telemetry", "timdr_candidate"):
        assert set(result[name]) == {
            "tp", "fp", "fn", "tn", "precision", "recall", "f1",
            "false_positive_rate",
        }


def test_benchmark_metrics_are_reproducible():
    first = run()
    second = run()
    for key in (
        "status", "calibration_seeds", "holdout_seeds", "thresholds",
        "holdout_windows", "simple_telemetry", "timdr_candidate",
        "limitations",
    ):
        assert first[key] == second[key]


def test_candidate_is_not_claimed_as_better_than_simple_baseline():
    result = run()
    # Current synthetic run: drift feature raises false positives without
    # improving recall. This is an observed limitation, not a target to tune away.
    assert result["timdr_candidate"]["recall"] == result["simple_telemetry"]["recall"]
    assert result["timdr_candidate"]["false_positive_rate"] >= result["simple_telemetry"]["false_positive_rate"]
