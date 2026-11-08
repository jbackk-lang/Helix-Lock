from experiments.helix_resonance_filter import benchmark, decode
from experiments.helix_chiral_signal import transmit


def test_clean_signal():
    for symbol in range(4):
        obs = [transmit(symbol, 1, sensors=12, noise=0, seed=i) for i in range(3)]
        assert decode(obs, "circular") == symbol
        assert decode(obs, "resonance") == symbol


def test_matched_report():
    a = benchmark(sizes=(8,), trials=2, noise_levels=(0.9,), repeats=(3,),
                  corruption_rates=(0.15,))
    b = benchmark(sizes=(8,), trials=2, noise_levels=(0.9,), repeats=(3,),
                  corruption_rates=(0.15,))
    assert len(a["results"]) == 2
    for x, y in zip(a["results"], b["results"]):
        assert x["symbol_accuracy"] == y["symbol_accuracy"]
        assert x["whole_file_success"] == y["whole_file_success"]
