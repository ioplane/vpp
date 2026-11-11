# ADR-0004: Native drivers and DPDK

Status: accepted. Date: 2026-11-11.

## Context

VPP supports NICs through the DPDK plugin and through native drivers. Since
`38c619115` ("dev: new device driver infra", 2023-10-17) native drivers share
one framework in `src/vnet/dev`. The DPDK plugin is still maintained: it is
pinned to DPDK 26.07 and received 38 commits in 2026.

Commits per year touching the DPDK plugin versus native driver code, measured
on upstream `242ab5bfe`:

| Year | DPDK plugin | Native drivers |
|---|---|---|
| 2022 | 69 | 0 |
| 2023 | 34 | 22 |
| 2024 | 24 | 64 |
| 2025 | 18 | 49 |
| 2026 | 38 | 142 |

The framework commit has no message body, so the reasons come from the
`vpp-dev` list:

- Damjan Marion, 2019, thread "ethernet-input on master": "DPDK is suboptimal
  for our use case, and with native implementation it is easy to show that",
  and, asked whether AVF would replace DPDK drivers: "I don't think we want to
  be in device driver business, unless device vendors pick it up, but on other
  side it is good to have one native implementation".
- Damjan Marion, December 2019, thread "efficient use of DPDK": "DPDK i40e
  driver provides 18.62 Mpps" against "native AVF driver is giving us arounf
  24.86 Mpps", and "you cannot use dpdk drivers without using EAL, mempool,
  rte_mbuf".
- Jerome Tollet, same thread: "native drivers (like Mellanox or AVF) can be
  faster w/o buffer conversion".
- Benoit Ganne, 2021-11-09: DPDK "has performance impacts and also carries a
  lot of dependencies"; without mandatory DPDK, a RISC-V port needs only VPP.
- Damjan Marion, 2021-11-22: "native AVF driver 22.5 Mpps vs DPDK i40e
  17.5Mpps on the same hardware", and "As long as DPDK stays as monolithic as
  it is, our only option is to have native drivers".
- Counter-view, Thomas Monjalon (DPDK), December 2019: "So why not improving
  DPDK integration in VPP to make it faster?" and "real performance benefits
  are in hardware device offloads which will be hard to implement in VPP
  native drivers".

## Decision

1. The fork does not add new functionality that only works with the DPDK
   plugin.
2. Device-facing work targets the `src/vnet/dev` framework where a native
   driver exists for the hardware.
3. The fork does not write new device drivers. That is work for hardware
   vendors and the framework maintainer.

## Rejected

- **Treating DPDK as deprecated.** Upstream has not said so, the plugin is
  maintained, and many NICs have no native driver.

## Consequences

Tests and lab setups of the fork use native drivers or software interfaces
(`pg`, `tap`, `memif`, `af_packet`) where possible, so results do not depend
on a DPDK version.
