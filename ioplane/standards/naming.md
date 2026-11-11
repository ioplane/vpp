# Naming convention

Names used by the fork. Names inside upstream code follow upstream practice
and are not restated here.

## Character set

Branch names and file names use lowercase `a–z`, digits, `-`, and `/` as the
branch namespace separator. Dates are ISO 8601 basic, `YYYYMMDD`.

## Branches

```text
<kind>/<feature-id>-<slug>
```

| Slot | Values |
|---|---|
| `kind` | `fix`, `feat`, `test`, `docs`, `ci`, `review`, `backup` (closed list) |
| `feature-id` | a feature id from upstream `MAINTAINERS`, for example `ikev2`, `linux-cp`, `session` |
| `slug` | two to five words, hyphenated, naming the behaviour |

- `review/` holds a branch pushed only to run CI or to show a reviewer.
- `backup/` holds a ref taken before a rebase; it ends with `-YYYYMMDD`.
- `master` and `stable/NNNN` mirror upstream and receive no direct commits.

Examples: `fix/ikev2-sa-proposal-length`, `feat/ikev2-fragmentation`,
`docs/ioplane-roadmap`, `backup/linux-cp-route-delete-20261021`.

Branches created before this convention keep their names until they merge or
are deleted; no new branch uses another scheme.

## Documents

| Kind | Pattern |
|---|---|
| ADR | `ioplane/adr/NNNN-short-slug.md` |
| Design proposal | `ioplane/rfc/NNNN-short-slug.md` |
| Standard | `ioplane/standards/<topic>.md` |

Numbers have four digits and are never reused.

## Tests

A regression test class in `test/` is named for the behaviour it protects,
prefixed by the role under test where the module has roles:
`TestResponderMalformedProposal`, `TestInitiatorEarlyCreateChild`. The
docstring is one sentence stating the required behaviour, with the RFC section
when there is one.

## Gerrit changes

The subject is the commit subject; see
[coding-style.md](coding-style.md). The Gerrit topic of a stack is the branch
slug without the `kind/` prefix.

## Not in a name

Ticket numbers, author names, dates other than on `backup/` branches, and
status words such as `wip` or `final`.
