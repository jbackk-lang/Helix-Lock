import pytest
from experiments.helix_chiral_memory_inference import infer_labels, trial, run

def test_exact_reversal_inference_from_phase_history_with_first_sample_anchor():
    for flip in (0, 3, 6, 9, 12):
        for initial in (-1, 1):
            x = trial(41, flip_after=flip, initial_handedness=initial,
                      anchored=True, measurement_noise=0)
            assert x["label_accuracy"] == 1
            assert x["payload_exact_match"]

def test_unanchored_mirror_symmetry_is_unidentifiable():
    samples = [(0.4, 1.2), (0.41, 1.18), (-0.4, -1.2)]
    plus = infer_labels(samples, initial_handedness=1)
    minus = infer_labels(samples, initial_handedness=-1)
    assert plus == [-h for h in minus]
    assert infer_labels(samples, initial_handedness=None) in (plus, minus)

def test_reproducible_summary_and_expected_shape():
    x = run([10, 11], noise_levels=(0.08,))
    assert x == run([10, 11], noise_levels=(0.08,))
    assert len(x["summary"]) == 10

def test_input_validation():
    with pytest.raises(ValueError):
        infer_labels([])
    with pytest.raises(ValueError):
        infer_labels([(0.1, 0.2)], initial_handedness=0)
    with pytest.raises(ValueError):
        trial(1, flip_after=13)
