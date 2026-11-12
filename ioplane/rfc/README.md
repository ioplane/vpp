# Design proposals

A proposal (called RFC here, not to be confused with an IETF RFC) describes a
roadmap item that needs agreement before code: a new protocol feature, a new
API, or a change of behaviour. A bug fix needs no proposal.

- File name: `NNNN-short-slug.md`, four digits, numbered in order of creation.
- Status is one of `draft`, `discussed on vpp-dev`, `accepted`, `withdrawn`.
- A proposal is taken to the `vpp-dev` list and the plugin maintainer before
  the first change is pushed to Gerrit.

## Required sections

| Section | Content |
|---|---|
| Summary | One paragraph: what changes for a user |
| Normative references | IETF RFC sections the work implements |
| Current behaviour | What upstream does today, with file references |
| Proposed behaviour | Wire format, state machine, API and CLI changes |
| Failure handling | Every new failure path and what the peer or caller sees |
| Test plan | Regression tests, negative tests at input boundaries, interop peer |
| Compatibility | Behaviour against a peer or client without the feature |
| Out of scope | What is deliberately not done |

| RFC | Title | Status |
|---|---|---|
| [0001](0001-ikev2-fragmentation.md) | IKEv2 message fragmentation | draft |
| [0002](0002-linux-cp-nexthop-objects.md) | Nexthop objects in linux-cp | draft |
| [0003](0003-ikev2-signature-authentication.md) | IKEv2 signature authentication | draft |
