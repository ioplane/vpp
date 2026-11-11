# ADR-0002: IKEv1 is not implemented

Status: accepted. Date: 2026-11-11.

## Context

VPP implements IKEv2 only. Commercial gateways still ship IKEv1 next to IKEv2,
and interoperability with old peers is a recurring request.

- RFC 9395 (April 2023, Standards Track) deprecates IKEv1 and moves RFC 2407,
  RFC 2408 and RFC 2409 to Historic. It states that IKEv1-only systems should
  be upgraded or replaced by systems supporting IKEv2.
- IKEv1 is a different protocol, not a mode of IKEv2: two phases, main and
  aggressive mode, its own payload and state machine. Nothing in
  `src/plugins/ikev2` can be reused except crypto helpers.
- The IKEv2 plugin itself is still `state: experimental` and lacks
  fragmentation (RFC 7383), cookies, signature authentication (RFC 7427) and
  post-quantum preshared keys (RFC 8784).

## Decision

IKEv1 is not implemented and is not accepted as a roadmap item. Effort goes to
closing the IKEv2 gaps listed in [ROADMAP.md](../ROADMAP.md).

## Rejected

- **Full IKEv1.** A second key-exchange daemon to secure, test and maintain for
  a protocol the IETF has retired. Aggressive mode with preshared keys exposes
  a hash that can be attacked offline, so adding it lowers the security
  baseline of every deployment that enables it.
- **IKEv1 main mode only, as a migration aid.** Still a full second state
  machine; the saving is small and the maintenance cost is the same.

## Consequences

A deployment that must reach an IKEv1-only peer terminates that tunnel on an
external IKE daemon and programs the resulting SAs into VPP through the IPsec
API. This path exists today and needs no change in VPP.

The decision is revisited only if a maintainer of the IKEv2 plugin asks for
IKEv1 with a concrete deployment behind the request.
