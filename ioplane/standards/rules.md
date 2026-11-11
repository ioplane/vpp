# Rules for contributing through the fork

These rules apply to every change staged in `ioplane/vpp` before it goes to
`gerrit.fd.io`.

## Before code

1. The work is an item in [ROADMAP.md](../ROADMAP.md) or a bug with a
   reproduction. New features start with a
   [design proposal](../rfc/README.md).
2. A defect is confirmed on current upstream `master`, not on a stable or
   topic branch, before it is called a defect.

## While coding

3. Bug fixes are test-first: the regression test fails on the unpatched tree
   for the stated reason and passes with the fix.
4. One logical change per commit. Refactoring and formatting of untouched
   code go in separate commits or not at all.
5. Style follows [coding-style.md](../standards/coding-style.md); names follow
   [naming.md](../standards/naming.md).

## Before push to Gerrit

6. `make checkstyle` is clean and the build succeeds.
7. The test module of the touched feature passes, not only the new test.
8. The commit touches only files under `src/`, `test/`, `docs/` or `extras/`
   that belong to the change. Editor and tool configuration is never
   committed.
9. The commit message carries no tool or assistant attribution.

## In review

10. A review comment is answered in its thread and the thread is resolved
    when the next patch set addresses it.
11. A change is amended in place; it is not abandoned and recreated to tidy
    history.
12. A failed CI vote is read before `recheck` is sent: if the failing job
    never ran the code, recheck; otherwise reproduce first.
13. Changes of a large stack are rechecked one at a time.

## Security

14. A defect that a remote unauthenticated peer can trigger is reported to the
    upstream security team as `SECURITY.md` requires. It is not pushed to a
    public branch, described in a public issue or mentioned in a commit
    message before the upstream team agrees.

## Documents

15. A decision that will be questioned again is recorded as an
    [ADR](../adr/README.md) in the same change that acts on it.
16. `ROADMAP.md` is updated when an item changes status.
