# Synthetic channel controls for a helically phased signal

This extension to `HELIX_CHIRAL_SIGNAL.md` tests **shared phase drift** and **coherent opposite-winding echoes**. A single time snapshot models Doppler only as a common phase offset; it does not model the full time-dependent Doppler frequency shift. A synthetic reflected component has phase winding opposite to the direct signal. The complex fields are added before phase extraction.

**Hypotheses and controls**
- Without a phase pilot, a pi/2 common drift rotates a QPSK symbol; chirality can remain readable.
- With a calibrated phase pilot, the same payload can be recovered.
- When the opposite-winding echo exceeds the direct component, the decoder may prefer the reflected handedness; the observed sign is not necessarily the emitter's sign.
- Sweeps: phase 0/pi/2, echo amplitudes 0/0.3/0.8/1.2, calibrated versus uncalibrated reference, 200 deterministic seeds.

**Run:** `python -m experiments.helix_chiral_signal_channel --output helix-chiral-signal-channel.json`

This is a falsifiable simulation of phase decoding, not empirical evidence of a universal helix of natural signals. Next physical step: explicit source/receiver trajectories and frequency-dependent propagation.
