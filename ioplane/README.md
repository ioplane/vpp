# ioplane fork of FD.io VPP

This directory holds everything that is specific to the `ioplane/vpp` fork:
the roadmap, the decisions behind it and the working rules. It is written for
people who contribute through this fork and for upstream reviewers who want to
see where a change comes from. After reading it you know what the fork plans to
send upstream, why, and which rules a change must satisfy first.

The fork carries no private features. Every code change here is meant for
`gerrit.fd.io`; the fork exists to stage, test and review work before it is
pushed there.

| Document | Purpose |
|---|---|
| [ROADMAP.md](ROADMAP.md) | Planned work, ordered, each item tied to an IETF RFC or a measured gap |
| [adr/](adr/README.md) | Architecture decision records: what was decided and what was rejected |
| [rfc/](rfc/README.md) | Design proposals for items that need agreement before code |
| [standards/coding-style.md](standards/coding-style.md) | Code and commit style, as enforced upstream |
| [standards/naming.md](standards/naming.md) | Names of branches, documents, tests and changes |
| [standards/rules.md](standards/rules.md) | Rules for contributing through the fork |

Owner: Pavel Lavrukhin. Last reviewed: 2026-11-12, against upstream
`242ab5bfe` (`v27.02-rc0-422`).
