# ADR-0001: Fork purpose and branch model

Status: accepted. Date: 2026-11-11.

## Context

VPP is developed on `gerrit.fd.io`; GitHub `FDio/vpp` is a mirror. Changes are
reviewed one commit at a time and need `Verified+1` from CI and
`Code-Review+2` from a maintainer. A fork is useful for staging stacks of
changes, running extra analysis and keeping planning documents, but a fork that
accumulates private patches diverges and stops being reviewable.

## Decision

1. The fork carries no feature that is not intended for upstream.
2. `master` of the fork follows upstream `master`. Fork-only material lives in
   the `ioplane/` directory and in CI workflow files.
3. Work happens on topic branches named by
   [standards/naming.md](../standards/naming.md); each branch maps to one
   Gerrit change or one stack of dependent changes.
4. A change is pushed to Gerrit only after the checks in
   [standards/rules.md](../standards/rules.md) pass.
5. Security defects that an unauthenticated peer can trigger are reported
   privately as `SECURITY.md` of upstream requires, and are not pushed to any
   public branch before the upstream security team agrees.

## Rejected

- **Long-lived product branch with private patches.** Every upstream release
  then costs a rebase, and fixes reach other users late or never.
- **Planning documents in a separate repository.** They drift from the code;
  next to the code they change in the same review.

## Consequences

The fork can be deleted at any time without losing functionality; only the
planning documents and unmerged topic branches would be lost.
