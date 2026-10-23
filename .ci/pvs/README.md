# PVS-Studio NAT/IKE analysis

Fork-only integration; no upstream FD.io runner or production deployment.
Analyze the trusted `ci/pvs-studio-2026-10-24` branch with native Clang in
Podman. The build receives no license. The network-disabled analysis container
receives `PVS_LICENSE_B64`: base64 of the documented two-line Linux license file.
Store it as a GitHub Actions secret and a masked, protected GitLab variable.
Never enable this workflow for untrusted pull requests.

The scope is five NAT44-ED/IKE translation units, not the full VPP tree.
V522 positive control, exact input count, analyzer exit status, preprocessing
errors and FAIL diagnostics are blocking. Existing GA diagnostics are reported
without suppressions; a passing job is not a clean security review.
Artifacts contain sanitized JSON, SARIF, GitLab Code Quality and totals.
The license and raw analyzer logs remain in tmpfs and are not uploaded.

Source: [PVS-Studio full manual](https://pvs-studio.com/en/docs/manual/full/),
retrieved 2026-10-24: GitHub Actions, GitLab CI/CD, Linux licensing,
JSON Compilation Database and plog-converter sections. Markdown snapshot SHA256:
`c11b33bff0ccb8f8e02df2b73de29165c8ef35f9cf28adc4bae76f87bc0f4464`.
