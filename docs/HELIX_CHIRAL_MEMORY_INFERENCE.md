# Infer handedness changes from phase history

This experiment tests whether a two-state continuity decoder can infer **when** the local helix phase orientation changed, without being handed the full left/right label sequence. It optionally knows the handedness of the **first** sample as a calibration anchor. The flip boundary is hidden from the decoder.

A Viterbi dynamic program minimizes the sum of squared circular phase jumps in canonical coordinates plus a penalty for orientation changes. Two phase coordinates are observed at each step.

## Identifiability limitation

The phase codebook is symmetric under global sign. Therefore `(h_t, phi)` and `(-h_t, -phi)` produce exactly the same observations. Without any external orientation anchor, absolute chirality and the canonical payload cannot be jointly identified. Reporting modulo-global-sign label accuracy prevents falsely presenting a choice of sign as an observation.

## Controls

- Five reversal boundaries including no-reversal endpoints.
- First-sample handedness known versus unknown.
- Measurement noise 0.08, 0.2 and 0.4 rad.
- 100 paired seeds by default.
- Exact payload recovery, label accuracy, label accuracy modulo global sign, circular phase error.

The experiment assumes two constant canonical phase symbols and an abrupt sign reversal. It does not derive a physical torsion measurement or show that a real helical memory system follows this law.

Run `python -m experiments.helix_chiral_memory_inference --output helix-chiral-memory-inference.json`.
