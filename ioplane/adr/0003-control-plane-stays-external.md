# ADR-0003: The control plane stays outside VPP

Status: accepted. Date: 2026-11-11.

## Context

VPP has no routing protocol implementation: no BGP, OSPF, IS-IS, LDP or PIM
directory exists under `src/` at `242ab5bfe`. Routes arrive through the binary
API or through the `linux-cp` plugin, which mirrors Linux netlink state
(links, addresses, neighbours, IPv4/IPv6/MPLS routes) into the FIB. The
plugin's own description states the model: Linux is the network stack with
the control-plane protocols, VPP is the forwarding engine.

FRR can also export its FIB over FPM. VPP has no FPM consumer: `git grep -lw
fpm src/` returns nothing.

## Decision

1. No routing protocol is added to VPP by this fork.
2. Integration with routing daemons goes through `linux-cp`. The fork invests
   in bringing that plugin from `experimental` to `production`.
3. No FPM consumer is built without a named operator who needs it.

## Rejected

- **Routing protocols as plugins.** Duplicates mature daemons and moves
  protocol security exposure into the forwarding process.
- **FPM consumer now.** FRR's `dplane_fpm_nl` carries netlink route messages
  over TCP. The linux-cp listener already handles netlink overrun and resync,
  so an FPM consumer would add a second ingestion path for the same data,
  while the host interfaces that linux-cp creates are still needed for the
  routing daemon to run its protocols.

## Consequences

Gaps between what the kernel can express and what linux-cp consumes become
roadmap items: nexthop objects, policy rules and VRF devices.
