# Helix Chiral Intelligence — isolated experimental prototype

**Current scope: Helix for Helix. TSI is deferred until access is available.**

`experiments/helix_chiral_intelligence.py` provides an independent observer with a typed `Observation` and `Assessment` interface. It does not modify production Helix-Lock, AIRP, authentication or cryptographic decisions.

Features:
- Estimate winding sign by comparing phase coherence of two spatial winding hypotheses after fitting a nuisance common phase separately for each.
- Abstain (`handedness=None`) if evidence or coherence is insufficient, including a one-sensor negative control.
- Decode a QPSK payload **only** with an explicit calibrated phase reference; otherwise return `chirality_only`.
- Maintain bounded history and flag changes in estimated winding or poor spatial coherence.
- Treat a strong opposite-winding reflection as a possible false *observed* handedness; the module does not authenticate the emitter.

**Limitations:** `evidence` is a score difference, not a calibrated posterior probability. A narrow angular aperture, multipath, unknown sensor orientation and time-varying Doppler require further validation. A reversal alert does not distinguish a source change from a reflection or frame change. No TSI integration.

**Tests:** `python -m pytest -q tests/test_helix_chiral_intelligence.py`.
