from experiments.timdr_benchmark import run


def test_benchmark_uses_disjoint_calibration_and_holdout_and_reports_metrics():
    result = run()
    assert result["status"] == "synthetic_exploratory_only"
    assert result["calibration_seeds"] == [1000, 1099]
    assert result["holdout_seeds"] == [9000, 9099]
    assert result["holdout_windows"] == 6400
    for name in ("simple_telemetry", "timdr_candidate"):
        assert set(result[name]) == {
            "tp", "fp", "fn", "tn", "precision", "recall", "f1",
            "false_positive_rate",
        }


def test_benchmark_is_reproducible():
    assert run() == run()
