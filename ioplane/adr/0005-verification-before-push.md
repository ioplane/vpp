# ADR-0005: Verification environment and gate before push

Status: accepted. Date: 2026-11-12.

## Context

Upstream CI is the only authority for `Verified+1`, but it is a shared
resource and has been unreliable in three different ways within one week of
November 2026:

- a checkstyle job waited 24 hours for a runner and was cancelled, which
  produced `Verified-1` on a change that was never built;
- a stack of 20 changes pushed at once produced `worker thread deadlock`
  panics in multi-worker tests; the same patch sets passed when rechecked one
  at a time;
- workflow runs ended with `startup_failure`, and one run whose test jobs all
  succeeded never posted its vote.

A red vote therefore does not always describe the change, and a recheck costs
about an hour of shared runners.

## Decision

1. Every change is built and tested in a container before it is pushed. The
   container image is the toolchain; nothing is installed on the host.
2. The gate is: checkstyle with the clang-format version upstream uses, a
   debug build, and the complete test module of each touched feature.
3. The toolchain image is defined by a Containerfile kept with the
   organisation's other toolchain images, pinned by base image digest, and
   reads packages only from the organisation's mirrors.
4. A failed upstream vote is classified from the job logs before any action:
   if the failing job did not run the code, recheck; otherwise reproduce in
   the container first.
5. Dependent changes are pushed and rechecked in small groups, not as one
   batch.

## Rejected

- **Relying on upstream CI alone.** Feedback takes an hour, and its failures
  are not always about the change.
- **Building on the developer host.** Results then depend on whatever the
  host has installed and cannot be repeated by a reviewer.

## Consequences

The container must track what upstream CI uses for formatting and must be
able to run `make test`. Differences between the container's compilers and
libraries and those of upstream CI are recorded when found, because a newer
compiler or OpenSSL in the container is also an early warning for upstream.
