"""Release-blocking counterexample: correlated echo defeats vote independence."""
import math

from experiments.helix_reflection_stress import reflected_observation
from experiments.helix_symbol_consensus import decode_consensus
from experiments.helix_resonance_filter import decode
from experiments.helix_phase_coherence import decode_adaptive


def test_correlated_echo_is_not_independent_consensus_evidence():
    # Direct phasor + 0.85j yields phase bias atan(0.85) > pi/8.
    # All copies agree on the SAME biased phase.
    obs = [
        reflected_observation(0, echo_amplitude=0.85,
                              echo_phase=math.pi / 2, noise=0, seed=i)
        for i in range(7)
    ]
    assert decode_consensus(obs) != 0
    assert decode(obs, "circular") != 0
    assert decode_adaptive(obs)[0] != 0


def test_uncorrupted_reference_still_decodes():
    obs = [reflected_observation(0, echo_amplitude=0,
                                 echo_phase=math.pi / 2, noise=0, seed=i)
           for i in range(7)]
    assert decode_consensus(obs) == 0
