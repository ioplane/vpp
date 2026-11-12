# Architecture decision records

An ADR records one decision of the fork: the context, the choice, the options
that were rejected and what follows. Write an ADR when a roadmap item is
accepted or rejected for a reason that will be asked about again.

- File name: `NNNN-short-slug.md`, four digits, numbered in order of creation.
- Status is one of `proposed`, `accepted`, `superseded by NNNN`.
- An accepted ADR is not edited; a new ADR supersedes it.
- Facts cite their source: an RFC section, an upstream file and commit, or a
  dated mailing-list message.

| ADR | Title | Status |
|---|---|---|
| [0001](0001-fork-purpose-and-branch-model.md) | Fork purpose and branch model | accepted |
| [0002](0002-no-ikev1.md) | IKEv1 is not implemented | accepted |
| [0003](0003-control-plane-stays-external.md) | The control plane stays outside VPP | accepted |
| [0004](0004-native-drivers-and-dpdk.md) | Native drivers and DPDK | accepted |
| [0005](0005-verification-before-push.md) | Verification environment and gate before push | accepted |
| [0006](0006-signature-authentication-first.md) | Signature authentication is the next IKEv2 feature | accepted |
