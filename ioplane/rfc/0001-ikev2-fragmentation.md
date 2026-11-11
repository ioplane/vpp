# RFC-0001: IKEv2 message fragmentation

Status: draft. Date: 2026-11-11. Roadmap: section 1.

## Summary

An IKE_AUTH message that carries certificates can exceed the path MTU. VPP
then relies on IP fragmentation, which many networks and NAT devices drop, so
the exchange times out. RFC 7383 lets IKEv2 split an encrypted message into
several IKE messages. This proposal adds that to the VPP IKEv2 plugin.

## Normative references

- RFC 7383, IKEv2 Message Fragmentation: §2.3 negotiation, §2.5 fragmenting,
  §2.6 reassembly, §2.5.1 fragment size.
- RFC 7296 §2.1, retransmission; §3.14, Encrypted payload.

## Current behaviour

At upstream `242ab5bfe` the plugin knows the notify type
`IKEV2_FRAGMENTATION_SUPPORTED` only as an enumeration value in `ikev2.h`. It
neither sends nor honours it, and it has no Encrypted Fragment payload (type
53) parser or builder.

## Proposed behaviour

1. Send `IKEV2_FRAGMENTATION_SUPPORTED` in IKE_SA_INIT when a profile enables
   fragmentation; record the peer's notify on the IKE SA.
2. When both sides support it and an outgoing encrypted message exceeds the
   configured size, emit Encrypted Fragment payloads, each encrypted and
   integrity-protected on its own, with consecutive fragment numbers and the
   total count.
3. On receive, verify each fragment before storing it, reassemble when all
   fragments of one Message ID are present, then process the message as today.
4. Configuration: per-profile switch and fragment size; defaults follow the
   recommendations of RFC 7383 §2.5.1.

## Failure handling

- A fragment that fails integrity is dropped and counted; no state changes.
- Total-fragments mismatch within one Message ID discards the stored set as
  RFC 7383 §2.6 specifies.
- Reassembly state is bounded per IKE SA and released on timeout, on SA
  deletion and when a new Message ID starts. Only a peer that completed
  IKE_SA_INIT can create reassembly state, and that peer is not yet
  authenticated, so the bound applies before IKE_AUTH succeeds.
- Allocation failure aborts the exchange with an error counter; no partially
  reassembled message is processed.

## Test plan

- Regression: IKE_AUTH with a certificate chain larger than the fragment
  size, as initiator and as responder, IPv4 and IPv6.
- Boundaries: fragment number 0, number above total, total changed mid-set,
  duplicate fragment, fragments out of order, one fragment missing until
  timeout, total of 1.
- Retransmission of a fragmented request and of a fragmented response.
- Interoperability against strongSwan with `fragmentation = yes`.

## Compatibility

Without the peer's notify the plugin behaves exactly as today.

## Out of scope

Fragmentation of unencrypted IKE_SA_INIT messages (RFC 7383 does not cover
them), and the proprietary pre-standard fragmentation some vendors ship.
