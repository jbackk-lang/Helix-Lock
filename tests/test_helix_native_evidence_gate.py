from copy import deepcopy

from experiments.helix_native_evidence_gate import evaluate
from experiments.helix_native_history_comparison import compare


def sample_report():
    return {"metrics": {
        "instant": {"accuracy_with_abstentions": 0.70, "coverage": 0.95,
                    "reversal_delays": [0, 1, 0]},
        "history": {"accuracy_with_abstentions": 0.80, "coverage": 0.95,
                    "reversal_delays": [1, 2, 1]}}}


def test_candidate_gain_not_claimed_as_proof():
    result = evaluate(sample_report())
    assert result["verdict"] == "candidate_gain_not_proof"
    assert result["gain"] > 0


def test_accuracy_regression_flagged():
    report = sample_report()
    report["metrics"]["history"]["accuracy_with_abstentions"] = 0.5
    assert evaluate(report)["verdict"] == "tradeoff_or_regression"


def test_reversal_latency_tradeoff_flagged():
    report = sample_report()
    report["metrics"]["history"]["reversal_delays"] = [4, 5, 4]
    assert evaluate(report)["verdict"] == "tradeoff_or_regression"


def test_missing_reversal_is_not_hidden():
    report = sample_report()
    report["metrics"]["history"]["reversal_delays"] = [None, 2, 1]
    result = evaluate(report)
    assert result["history_missed_reversals"] == 1
    assert result["verdict"] == "tradeoff_or_regression"


def test_no_improvement_inconclusive():
    report = sample_report()
    report["metrics"]["history"]["accuracy_with_abstentions"] = 0.70
    assert evaluate(report)["verdict"] == "inconclusive"


def test_real_comparison_is_classified_and_repeatable():
    report = compare(seeds=range(3), samples=12, window=3)
    assert evaluate(report) == evaluate(report)
    assert evaluate(report)["verdict"] in {
        "candidate_gain_not_proof", "tradeoff_or_regression", "inconclusive"}
