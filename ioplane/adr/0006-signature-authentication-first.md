# ADR-0006: Signature authentication is the next IKEv2 feature

Status: accepted. Date: 2026-11-12.

## Context

The roadmap of 2026-11-11 ordered new IKEv2 work as fragmentation, cookies,
then signature authentication (milestones M4 and M6). Three facts found on
2026-11-12 change the weights.

1. Certificate authentication in the plugin is method 1 only, RSASSA-PKCS1-v1_5
   with SHA-1: `ikev2_calc_sign ()` and `ikev2_verify_sign ()` in
   `src/plugins/ikev2/ikev2_crypto.c` pass `EVP_sha1 ()` unconditionally, and
   `foreach_ikev2_auth_method` in `ikev2.h` lists `rsa-sig` and
   `shared-key-mic` only (upstream `1b2924c8e`).
2. Measured in the toolchain container (Fedora 46, OpenSSL 4.0.3, default
   crypto policy): `EVP_SignFinal ()` with SHA-1 returns 0 and
   `EVP_VerifyFinal ()` returns -1, "invalid digest". Method 1 therefore
   cannot authenticate on a host whose policy forbids SHA-1 signatures;
   `test_ikev2.TestResponderRsaSign` fails there and passes once the policy
   allows SHA-1. Change 47688 makes that failure explicit; it does not make
   certificate authentication work.
3. The initiator already announces the feature it lacks. `ikev2.c` adds a
   `SIGNATURE_HASH_ALGORITHMS` notify with the identifiers 1, 2, 3, 4 (SHA-1,
   SHA2-256, SHA2-384, SHA2-512) to every IKE_SA_INIT request, and no code
   reads the peer's notify or handles authentication method 14. RFC 7427 §4
   says the notify "implicitly indicates support of the new Digital Signature
   algorithm method", and §3 says that when both ends exchange it and
   signature authentication is used, method 14 "MUST be used". Whether common
   peers then answer with method 14 is not measured yet.
4. The signing code is not limited to RSA keys. Measured with an EC P-256
   key: `EVP_SignFinal ()` with SHA-1 succeeds where SHA-1 is allowed, so an
   ECDSA signature leaves the plugin labelled as method 1, "RSA Digital
   Signature".

The standards position: RFC 8247 §3.1 keeps method 1 at MUST "for
interoperability" and expects it "to be replaced with the generic Digital
Signature method"; §3.2 puts SHA-1 at MUST NOT and SHA2-256 at MUST for that
method, and requires RSASSA-PSS when it is used with RSA.

Review capacity is the constraint on everything: 46 changes of this fork are
open on Gerrit, 20 of them a stack in `ikev2.c`, and 45 of the 46 carry no
Code-Review vote on 2026-11-12.

## Options and weights

Scores are 1 (worst) to 5 (best). Weights sum to 100.

| Criterion | Weight | Meaning |
|---|---|---|
| Effect | 30 | what stops failing for a user once it is merged |
| Evidence | 20 | measurement or source in hand, not an expectation |
| Review cost | 20 | size, and conflict with the open stack and its reviewers |
| Implementation risk | 15 | size and number of new states |
| Verifiable here | 15 | can be proven in the container before push ([ADR-0005](0005-verification-before-push.md)) |

| Option | Effect | Evidence | Review | Risk | Verifiable | Total |
|---|---|---|---|---|---|---|
| Signature authentication, RFC 7427 | 5 | 5 | 2 | 3 | 4 | 3.95 |
| linux-cp nexthop objects, step 1: measurement only | 3 | 3 | 5 | 5 | 4 | 3.85 |
| Fuzz targets for external-input parsers | 3 | 4 | 3 | 3 | 5 | 3.50 |
| `worker thread deadlock` in parallel test runs | 4 | 3 | 4 | 3 | 2 | 3.35 |
| Cookies, RFC 7296 §2.6 | 3 | 3 | 3 | 4 | 4 | 3.30 |
| Fragmentation, RFC 7383 | 4 | 3 | 2 | 2 | 3 | 2.95 |

Reading of the scores:

- Signature authentication is the only option where the plugin is measured
  to fail today and where it also misstates its capabilities on the wire.
- The nexthop measurement scores almost the same for the opposite reason: it
  is cheap and touches neither the plugin code nor the open stack, but it
  repairs nothing by itself.
- Fragmentation keeps its user value and loses on size: it is the largest
  item and lands in the same file as the 20 open changes.

## Decision

1. Signature authentication (RFC 7427, method 14) is the next IKEv2 feature.
   It moves ahead of fragmentation and cookies.
   [RFC-0003](../rfc/0003-ikev2-signature-authentication.md) defines it.
2. Its first step is a measurement, not code: an interoperability run of the
   unmodified plugin against a peer that implements RFC 7427, as initiator
   and as responder. The result decides whether the announcement in fact 3
   is a present defect that needs its own small fix.
3. Code for RFC-0003 is pushed only after the proposal has been sent to the
   plugin maintainers, and it is based on 47688, not on the open stack.
4. The linux-cp nexthop measurement (roadmap M2) stays where it is and runs
   in parallel: it competes for neither the code nor the reviewers.
5. Fragmentation follows signature authentication; cookies follow
   fragmentation. Neither is dropped.

## Rejected

- **Fragmentation first, as planned.** No measurement of a failure exists
  for it, and it is the most expensive item to review.
- **Only stop sending the notify.** It would make the announcement honest
  and leave certificate authentication unusable where SHA-1 is forbidden. It
  remains the fallback if the proposal is not accepted.
- **Sign method 1 with SHA-2.** RFC 7296 §3.8 does not forbid it, but says
  implementations "SHOULD use SHA-1 as the default hash function when
  generating signatures" and gives no way to learn what the peer accepts.
  RFC 7427 §1 exists to close exactly that gap. Accepting a SHA-2 signature
  in method 1 on receive is a separate, compatible step and is part of
  RFC-0003.
- **Pause new work until the queue is reviewed.** The queue depends on other
  people; a proposal and a measurement add nothing to it.

## Consequences

- Roadmap milestones are renumbered: signature authentication becomes M4,
  fragmentation M5, fuzz targets M6, cookies M7.
- The work adds an ASN.1 `AlgorithmIdentifier` comparison to the plugin.
  RFC 7427 §3 allows treating the known encodings as opaque byte strings, so
  no ASN.1 parser is added.
- The test peer in `test/test_ikev2.py` needs method 14 as well; without it
  the feature cannot be tested in `make test`.
- Until the feature lands, deployments on hosts that forbid SHA-1 signatures
  have shared-key authentication only.
- This decision is revisited if the measurement of step 2 shows that peers
  ignore the announcement and keep using method 1: the effect score then
  drops to 4, the total to 3.65, and the nexthop measurement ranks first.
