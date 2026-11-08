# TSI hypothesis: spatially helical signal phase

**Scope:** A falsifiable *synthetic* communications model, not an astronomical claim that every signal is helical.

The transmitted phase is `phi(theta)=m*theta+phi_symbol+phi_offset+noise` with signed winding `m=+1/-1` and four payload phases (QPSK). A circular receiver array jointly estimates winding and symbol by correlation. Controls: 1/2/4/12 sensors, narrow versus full angular aperture, noise 0/0.12/0.4 rad, unknown versus calibrated common phase, and angle-reflection mirror symmetry.

**Identifiability:** At a single angular sample, both winding signs predict the same phase (score margin zero). With angular diversity the winding can be resolved. An unknown common phase offset of pi/2 can shift all decoded QPSK symbols while leaving the winding estimate intact. This separates *chirality sensing* from *payload phase calibration*. The direction sign is defined relative to an oriented receiver coordinate axis, not a universal cosmic right/left preference.

**Reproduce:** `python -m experiments.helix_chiral_signal --output helix-chiral-signal.json`.

**Limitations:** no physical helix antenna, propagation dynamics, moving source, Doppler, multipath, or galactic inference. A structured phase field is not necessarily a helical trajectory of energy or information.
