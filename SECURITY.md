# Security policy

## Supported security scope

Helix-Lock is currently in preparation for a closed beta. It is not a stable release and has not undergone an independent security audit. Experimental modules and formats are not part of the supported release surface unless explicitly documented.

## Reporting a vulnerability

**Do not report exploitable security vulnerabilities in public GitHub issues.**

Use GitHub's private vulnerability reporting for this repository if it is enabled:
https://github.com/jbackk-lang/Helix-Lock/security/advisories/new

If private reporting is unavailable, contact the repository maintainers through a verified contact channel published by the project. Do not guess or use an unverified address.

Please include:
- affected version or commit;
- affected platform and configuration;
- concise reproduction steps using disposable test data;
- impact and realistic attack preconditions;
- any proposed mitigation, if known.

Do not include real user files, plaintext, passwords, key files, private keys, recovery material or memory dumps. Do not publicly disclose exploit details before coordinating a fix.

## Beta tester safety

- Test only with disposable copies and maintain independent backups.
- Never use a beta build as the sole protection for important data.
- Do not disable operating-system security controls to run an unsigned build.
- Sanitise logs before sharing; logs must not contain secrets or file contents.

## Response

The maintainers will attempt to acknowledge reports, reproduce the issue, assess severity, prepare a fix and add regression coverage where practical. No response-time SLA is promised during the beta preparation phase.
