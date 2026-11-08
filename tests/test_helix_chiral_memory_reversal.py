import pytest
from experiments.helix_chiral_memory_reversal import run, run_trial

@pytest.mark.parametrize("flip_after", [0, 3, 6, 9, 12])
@pytest.mark.parametrize("start_h", [-1, 1])
def test_per_sample_normalization_preserves_mirror_paired_payload(flip_after, start_h):
    x = run_trial(42, flip_after=flip_after, start_handedness=start_h, readout="per_sample")
    y = run_trial(42, flip_after=flip_after, start_handedness=-start_h, readout="per_sample")
    assert x["payload_exact_match"] == y["payload_exact_match"]
    assert x["mean_reference_error_rad"] == pytest.approx(y["mean_reference_error_rad"], abs=1e-8)
    assert x["mean_final_error_rad"] == pytest.approx(y["mean_final_error_rad"], abs=1e-8)

def test_per_sample_labels_outperform_single_final_label_at_midpoint():
    seeds = range(1000, 1100)
    per_sample = [run_trial(s, flip_after=6, readout="per_sample")["mean_reference_error_rad"] for s in seeds]
    final_only = [run_trial(s, flip_after=6, readout="final_only")["mean_reference_error_rad"] for s in seeds]
    assert sum(per_sample) < sum(final_only)

def test_no_flip_final_only_equals_per_sample():
    for flip_after in (0, 12):
        x = run_trial(12, flip_after=flip_after, readout="per_sample")
        y = run_trial(12, flip_after=flip_after, readout="final_only")
        assert x["mean_reference_error_rad"] == pytest.approx(y["mean_reference_error_rad"])

def test_reversal_summary_is_reproducible():
    assert run([7, 8]) == run([7, 8])
    assert len(run([7, 8])["results"]) == 40

def test_invalid_reversal_inputs():
    with pytest.raises(ValueError):
        run_trial(1, flip_after=13)
    with pytest.raises(ValueError):
        run_trial(1, readout="unknown")
    with pytest.raises(ValueError):
        run_trial(1, start_handedness=0)

def test_shuffled_handedness_labels_are_worse_than_true_labels_at_midpoint():
    seeds = range(1000, 1100)
    correct = [run_trial(s, flip_after=6, readout="per_sample")["mean_reference_error_rad"]
               for s in seeds]
    shuffled = [run_trial(s, flip_after=6, readout="shuffled_labels")["mean_reference_error_rad"]
                for s in seeds]
    assert sum(correct) < sum(shuffled)


def test_shuffled_labels_have_no_effect_without_a_flip():
    for flip_after in (0, 12):
        x = run_trial(17, flip_after=flip_after, readout="per_sample")
        y = run_trial(17, flip_after=flip_after, readout="shuffled_labels")
        assert x["mean_reference_error_rad"] == pytest.approx(y["mean_reference_error_rad"])
