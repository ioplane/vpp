# Roadmap

Planned upstream contributions of the `ioplane/vpp` fork. An item enters this
list only with a reference: an IETF RFC section, an upstream file, or a
measurement. Order is by benefit to other VPP users, then by review cost.

Baseline: upstream `242ab5bfe` (`v27.02-rc0-422`), 2026-11-11. Last update:
2026-11-12. Maturity values
are the `state` field of the plugin's `FEATURE.yaml` at that commit.

## Status legend

| Status | Meaning |
|---|---|
| in review | change is on gerrit.fd.io |
| planned | accepted for work, no change yet |
| proposal | needs an [RFC document](rfc/README.md) first |
| rejected | see the linked ADR |

## 1. IKEv2 (`src/plugins/ikev2`, state: experimental)

| Item | Reference | Status |
|---|---|---|
| Reject inconsistent SA proposal length | RFC 7296 §3.3 | in review, 47638 |
| CREATE_CHILD_SA only after authentication | RFC 7296 §1.3 | in review, 47639 |
| Parallel Child SAs, rekey of the named Child | RFC 7296 §1.3.3, §2.8 | in review, 47647–47651 |
| Delete on failed rekey install, unknown Child rekey | RFC 7296 §2.21, §2.25 | in review, 47652–47656 |
| USE_TRANSPORT_MODE negotiation | RFC 7296 §1.3.1 | in review, 47112 |
| Message fragmentation | RFC 7383 | proposal, [RFC-0001](rfc/0001-ikev2-fragmentation.md) |
| Cookie exchange under load | RFC 7296 §2.6 | planned |
| Fail authentication when signing fails | RFC 7296 §2.15 | in review, 47688 |
| Do not announce signature hash algorithms without method 14 | RFC 7427 §3, §4 | in review, 47691 |
| Signature authentication with SHA-2, RSA-PSS and ECDSA | RFC 7427, RFC 8247 §3.2 | proposal, [RFC-0003](rfc/0003-ikev2-signature-authentication.md); next, [ADR-0006](adr/0006-signature-authentication-first.md) |
| Post-quantum preshared keys | RFC 8784 | planned |
| Intermediate exchange, multiple key exchanges | RFC 9242, RFC 9370 | proposal |
| Factor duplicated SA dump copies in the API | — | in review, 47682 |
| Section-to-test conformance table, then state → production | RFC 7296 | planned, after the stack merges |
| IKEv1 | RFC 2409 (Historic) | rejected, [ADR-0002](adr/0002-no-ikev1.md) |
| MOBIKE, EAP, configuration payload | RFC 4555, RFC 7296 §2.16, §2.19 | not planned without a remote-access user |

## 2. Linux control-plane integration (`src/plugins/linux-cp`, state: experimental)

| Item | Reference | Status |
|---|---|---|
| Release netlink socket and link on every path | libnl `nl_socket_free` | in review, 47520 |
| Reject malformed routes atomically | — | merged, 47337 |
| Native nexthop objects (`RTM_NEWNEXTHOP`, route `nh-id`) | kernel `rt-nexthop` netlink spec | proposal, [RFC-0002](rfc/0002-linux-cp-nexthop-objects.md) |
| Document the dependency on `nexthop_compat_mode` | kernel `ip-sysctl` | planned |
| Policy routing rules (`RTM_NEWRULE`) | kernel rtnetlink | proposal |
| VRF devices | kernel rtnetlink link kinds | proposal |
| Scale and churn tests, then state → production | — | planned |
| FPM consumer | — | rejected, [ADR-0003](adr/0003-control-plane-stays-external.md) |

## 3. Test and CI reliability

| Item | Reference | Status |
|---|---|---|
| `worker thread deadlock` panics under parallel CI load | `test/asf/asfframework.py` sets `barrier-timeout 5` | planned: collect data, propose a measured change |
| Fuzz targets for IKEv2 payloads, DHCP options, linux-cp netlink | defects fixed in 47638, 47514, 47337 | planned |

## 4. Robustness of error paths

| Item | Reference | Status |
|---|---|---|
| DHCP client option parsing bounded to the packet | RFC 2132 | in review, 47514 |
| Session layer rollback on attach, mq and detach failures | — | 47509 merged; 47516–47518, 47521 in review |
| ACL collision-list rescans bounded | — | in review, 47511 |
| vat2 JSON read bounded and fail-closed | — | in review, 47510 |

## 5. Kubernetes dataplane

| Item | Reference | Status |
|---|---|---|
| cnat session affinity and connection draining | Kubernetes `sessionAffinity: ClientIP` | proposal |
| Flow export of verdict and NAT translation | RFC 7011 | proposal |

## 6. Milestones

Work is taken in this order. A milestone starts when the previous one has
met its exit condition or is blocked on review.

| Milestone | Content | Exit condition |
|---|---|---|
| M1 | Land the open changes: answer reviews, keep CI green | every open change merged or abandoned with a reason |
| M2 | linux-cp nexthop objects, [RFC-0002](rfc/0002-linux-cp-nexthop-objects.md) step 1 | tests show the behaviour with `nexthop_compat_mode` 1 and 0; result posted to the maintainers |
| M3 | linux-cp nexthop objects, step 2 | change on Gerrit with the test plan of RFC-0002 passing |
| M4 | IKEv2 signature authentication, [RFC-0003](rfc/0003-ikev2-signature-authentication.md) | step 1 interoperability result posted; proposal sent to the plugin maintainers; changes on Gerrit with the test plan passing under a crypto policy that forbids SHA-1 |
| M5 | IKEv2 fragmentation, [RFC-0001](rfc/0001-ikev2-fragmentation.md) | proposal agreed with the plugin maintainers; change on Gerrit with interoperability evidence |
| M6 | Fuzz targets for IKEv2 payloads, DHCP options, linux-cp netlink | targets build in the toolchain container and run for a fixed time without findings, or the findings are fixed |
| M7 | IKEv2 cookies | change on Gerrit with negative tests |

M1 depends on reviewers and runs in parallel with the others. M2 is first
among the new work because it is a measurement: it changes no plugin code and
its result decides the size of M3. M4 was moved ahead of fragmentation and
cookies by [ADR-0006](adr/0006-signature-authentication-first.md); its first
step is also a measurement and runs in parallel with M2.

All work follows [ADR-0005](adr/0005-verification-before-push.md): built and
tested in the toolchain container before push.

## 7. Not planned

Recorded so that the question is not reopened without new facts.

| Item | Decision |
|---|---|
| IKEv1 | [ADR-0002](adr/0002-no-ikev1.md) |
| Routing protocols or an FPM consumer inside VPP | [ADR-0003](adr/0003-control-plane-stays-external.md) |
| Depending on DPDK for new device support | [ADR-0004](adr/0004-native-drivers-and-dpdk.md) |
| io_uring as a packet datapath | kernel socket stack path, not L2 bypass; no in-tree user |
