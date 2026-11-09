# Helix Stream

> **STATUS: EXPERIMENTAL — NOT FOR PRODUCTION USE**
>
> Helix Stream is the research and engineering track for authenticated encryption of data while it is being transmitted. It is not a released network protocol, has not undergone an independent security audit, and must not be used to protect production traffic.

Helix Stream is being developed separately from the desktop file-encryption application. The goal is a small, bounded-memory component for messages and byte streams, with explicit framing, session boundaries, replay handling, and transport adapters.

**We do not design a new cipher.** Confidentiality and integrity must come from established AEAD implementations and reviewed key-establishment protocols. Experimental phase/synchronization ideas never decide whether ciphertext is trusted.

## Scope of this branch

- Incremental record processing and bounded buffering.
- Authenticated record metadata and explicit end-of-stream handling.
- Session-scoped sequence and replay policy.
- Key rotation and direction separation using established standards.
- Transport adapters only after the record/session contract is reviewed.
- Reproducible latency, throughput, CPU and memory benchmarks.

## Starting point

The branch starts from the Helix-Lock file application branch and retains the HNS1 experiment for comparison:

- `experiments/helix_stream_envelope.py` — bounded-memory authenticated file envelope, 64 KiB records, AES-256-GCM and authenticated final totals.
- `tests/test_helix_stream_envelope.py` — round-trip and tamper/truncation checks.
- `tests/test_helix_stream_stress.py` — 12 MiB bounded-heap and crash-safety tests.

HNS1 is a **file prototype**, not a network protocol. It does not implement peer authentication, key exchange, session lifecycle, replay protection across reconnects, flow control or transport handling.

## Current implementation

An initial record-layer prototype now exists in `helix_stream/records.py`:

- `RecordSealer` and `RecordOpener` use AES-256-GCM from the established `cryptography` library;
- records carry a type, monotonically increasing sequence and explicit ciphertext length;
- the authenticated associated data binds the session identifier and direction label;
- each data record is limited to 64 KiB;
- an authenticated final record closes the stream.

Focused tests run on Python 3.11 and 3.12 through [Helix Stream CI](https://github.com/jbackk-lang/Helix-Lock/actions/workflows/helix-stream-tests.yml).

This is a low-level prototype, not a production protocol. It assumes a fresh, independent session-direction key and does not implement key establishment, peer authentication, replay persistence across reconnects, flow control or network transport. A receiver may consume individually authenticated records before the final record arrives; applications must not mistake record authentication for proof that the whole stream completed.

## Architecture direction

1. **Record layer:** strict framing, length limits, authenticated metadata, sequence numbers.
2. **Session layer:** reviewed key establishment, per-direction keys, nonce uniqueness, rotation and explicit session lifetime.
3. **Stream API:** incremental input/output independent of GUI and filesystem.
4. **Transport adapters:** TCP/QUIC/WebSocket/IPC selected by actual requirements; prefer TLS 1.3 or QUIC when they already solve the problem.
5. **Measurement:** latency percentiles, throughput, CPU, memory, loss/retry behavior and reproducible baselines.

See [the engineering roadmap](docs/HELIX_STREAM_ROADMAP.md) for milestones, threat-model gates and acceptance criteria.

## Development rule

First make the record/session contract correct and testable. Then benchmark it. Only then consider optimization. No custom cipher, KDF, key exchange or unaudited cryptographic construction. No merge into `main` or the File branch without review and passing regression tests.

## Related branch

[Helix File — desktop application and file encryption](https://github.com/jbackk-lang/Helix-Lock/tree/experiment/helix-native)
