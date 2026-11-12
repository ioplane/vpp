# RFC-0003: IKEv2 signature authentication

Status: draft. Date: 2026-11-12. Roadmap: section 1. Step 1 is done; steps 2 and
3 are implemented for RSA keys and not yet on Gerrit.
Decision record: [ADR-0006](../adr/0006-signature-authentication-first.md).

## Summary

Certificate authentication in the VPP IKEv2 plugin signs and verifies with
RSA and SHA-1 only. On a host whose crypto policy forbids SHA-1 signatures
it does not work at all, and the plugin already tells peers that it supports
the newer scheme it does not implement. This proposal adds the Digital
Signature authentication method of RFC 7427 with SHA-2, for RSA and ECDSA
keys, and makes the announcement match the implementation.

## Normative references

- RFC 7427: §3 Authentication payload and the format of the Authentication
  Data; §4 `SIGNATURE_HASH_ALGORITHMS` notify; §5 selecting the public key
  algorithm; Appendix A, DER encodings of the common `AlgorithmIdentifier`
  objects.
- RFC 7296: §2.15 the octets that are signed; §3.8 Authentication payload
  and method 1.
- RFC 8247: §3.1 status of the authentication methods; §3.2 hash functions
  and signature schemes for Digital Signature (SHA-1 MUST NOT, SHA2-256
  MUST, SHA2-512 SHOULD, RSASSA-PSS MUST with RSA, RSASSA-PKCS1-v1_5 MAY).

## Current behaviour

At upstream `1b2924c8e`:

- `ikev2.h` defines two authentication methods, `rsa-sig` (1) and
  `shared-key-mic` (2). A received AUTH payload with any other method
  matches no profile in `ikev2_select_profile ()` and authentication fails.
- `ikev2_calc_sign ()` and `ikev2_verify_sign ()` in `ikev2_crypto.c` use
  `EVP_sha1 ()` for every signature. With a crypto policy that forbids
  SHA-1 signatures both calls fail (measured: Fedora 46, OpenSSL 4.0.3).
- The initiator adds a `SIGNATURE_HASH_ALGORITHMS` notify with the
  identifiers 1, 2, 3, 4 to every IKE_SA_INIT request, also for a profile
  that uses a shared key. The responder sends none. No code reads the
  notify from a peer.
- The local private key is one global key (`ikev2_set_local_key`), loaded
  with `PEM_read_PrivateKey ()`; the peer's public key comes from the
  certificate file of the profile. Neither path restricts the key type.
  Measured with an EC P-256 key: where SHA-1 is allowed, the signing calls
  succeed, so the plugin sends an ECDSA signature labelled as method 1,
  "RSA Digital Signature".
- The responder selects a profile only in IKE_AUTH (`ikev2_sa_auth ()`);
  during IKE_SA_INIT it has none.

## Proposed behaviour

### Step 1: measurement, no code change

Run the unmodified plugin against a peer that implements RFC 7427, with
certificate authentication, as initiator and as responder. Record which
authentication method the peer puts in its AUTH payload after it has seen
the notify from VPP, and whether the exchange completes. The result is
posted with the proposal. If the peer answers with method 14 and the
exchange fails, the announcement is a present defect and step 2 is sent
first as its own fix.

Result, 2026-11-12. Peer: strongSwan 6.1.0, RSA-2048 certificates, both
daemons in one network namespace over a veth pair, SHA-1 signatures allowed
by the crypto policy so that method 1 can work at all.

| VPP | Initiator | Notify sent by VPP | Method used by the peer | Outcome |
|---|---|---|---|---|
| `1b2924c8e` | peer | no | 1 | established |
| `1b2924c8e` | VPP | yes: 1, 2, 3, 4 | 14, `sha256WithRSAEncryption` | VPP: `AUTH_FAILED`, "no matching profile found"; the peer reports the IKE SA as established |
| with 47691 | VPP | no | 1 | established |
| with 47691 | peer | no | 1 | established |

The Authentication Data of the peer under method 14 starts with
`0F 30 0D 06 09 2A 86 48 86 F7 0D 01 01 0B 05 00`: length 15 and the
`AlgorithmIdentifier` of RFC 7427 A.1.2. Three consequences:

- The announcement is a present defect: VPP as initiator with certificate
  authentication cannot connect to this peer. Change 47691 removes the
  notify; it is the small fix this step called for and does not replace
  steps 2 to 4.
- The peer signs RSASSA-PKCS1-v1_5 with SHA-256 by default, not RSASSA-PSS.
  Step 3 must accept that encoding to interoperate, which the table of
  accepted identifiers already does.
- The peer accepts method 1 from VPP even after both notifies were
  exchanged, and it ignores hash identifier 1 in the list from VPP.

### Step 2: make the announcement truthful

- The initiator knows its profile and sends `SIGNATURE_HASH_ALGORITHMS`
  only when that profile authenticates with a certificate.
- The responder has no profile during IKE_SA_INIT. It answers with the
  notify whenever the initiator sent one. This is a statement about the
  implementation, not about the profile chosen later; RFC 7427 §3 binds
  only an exchange in which "signature authentication is to be used".
- Both list only the hashes the plugin can verify: SHA2-256, SHA2-384,
  SHA2-512. SHA-1 (identifier 1) is not listed.
- The notify of the peer is parsed in IKE_SA_INIT and its set of hashes is
  kept on the IKE SA. A notify whose data length is not a multiple of two
  octets is a malformed message and fails the exchange.

Step 2 cannot be merged without step 3: once the notify is honest, a peer
may answer with method 14.

### Step 3: method 14

Which method a certificate profile uses follows RFC 7427 §3: method 14
when both ends sent the notify, method 1 otherwise.

| Profile | Both ends sent the notify | Notify missing on either side |
|---|---|---|
| `rsa-sig`, initiator | sends method 14; accepts method 14 or 1 | sends and accepts method 1, as today |
| `rsa-sig`, responder | accepts method 14 or 1; answers with the method the initiator used | sends and accepts method 1, as today |
| `digital-signature` (new) | sends and accepts method 14 only | authentication fails |

Two rules deviate from the "MUST be used" of RFC 7427 §3, on purpose:

- An `rsa-sig` profile accepts method 1 after the notify exchange. Releases
  of this plugin before 47691 announce the hashes and sign with method 1; a
  strict responder would lock them out.
- A responder answers with the method the initiator used. An initiator that
  signed with method 14 has shown that it implements it; one that announced
  the hashes and signed with method 1 would not understand a method 14
  answer.

Neither rule weakens anything against the code before this change: the
method is carried inside the protected IKE_AUTH exchange, and the previous
code accepted method 1 only. An `rsa-sig` profile does not gain protection
against attacks on SHA-1; `digital-signature` does.

An initiator verifies the responder against the profile it started the
exchange with, so a second profile cannot relax a `digital-signature` one.

- `digital-signature` (14) is one new value in the API enumeration and the
  CLI. It is the strict form for sites that must not use SHA-1, and it is
  the value the SA dump reports when method 14 was used.
- Signing with an RSA key: RSASSA-PSS with SHA-256 and a salt of 32 octets
  whenever the peer lists SHA2-256, which RFC 8247 §3.2 requires; otherwise
  RSASSA-PKCS1-v1_5 with the strongest hash the peer listed. ECDSA keys are
  a later step. The Authentication Data is the one-octet length, the DER
  `AlgorithmIdentifier` and the signature (RFC 7427 §3).
- Verifying: the `AlgorithmIdentifier` is compared as an octet string with
  a fixed table. From RFC 7427 Appendix A: RSASSA-PSS with SHA-256 (A.4.3),
  `sha256WithRSAEncryption`, `sha384WithRSAEncryption`,
  `sha512WithRSAEncryption` (A.1.2 to A.1.4) and `ecdsa-with-sha256`,
  `-sha384`, `-sha512` (A.3.2 to A.3.4). The appendix gives no encoding for
  RSASSA-PSS with SHA-384 or SHA-512; the table holds the same structure as
  A.4.3 with the hash, the MGF1 hash and the salt length replaced, and the
  octets a second implementation actually sends are recorded in the
  interoperability run before the table is fixed. Everything else,
  including every SHA-1 identifier and RSASSA-PSS with empty or default
  parameters, is rejected. No ASN.1 parser is added. The RSASSA-PSS
  identifier is also accepted in the 67-octet form a DER encoder writes,
  without the default trailerField; it is sent in the 72-octet form of the
  RFC.
- The algorithm must match the key type of the configured certificate, and
  an EC key is no longer signed under method 1.
- Signatures are computed with `EVP_DigestSign*` and `EVP_DigestVerify*`;
  every return value is checked, as in 47688.

### Step 4: method 1 on receive

`ikev2_verify_sign ()` accepts a method 1 signature made with SHA2-256,
SHA2-384 or SHA2-512 in addition to SHA-1. RFC 7296 §3.8 leaves the hash of
method 1 open and only recommends SHA-1 as the default. Signing with
method 1 is unchanged.

## Failure handling

| Condition | Result |
|---|---|
| Profile `digital-signature`, peer sent no notify | initiator: the SA is dropped before IKE_AUTH and an error is logged; responder: `AUTHENTICATION_FAILED` |
| Both ends sent the notify, peer's AUTH uses method 1 | accepted for an `rsa-sig` profile, `AUTHENTICATION_FAILED` for `digital-signature` |
| Profile `rsa-sig`, no notify exchanged, local key is not RSA | as "signing fails" below |
| No common hash with the peer's list | same as above |
| Received method 14, Authentication Data shorter than the length octet says | malformed message, exchange fails |
| `AlgorithmIdentifier` not in the accepted set | `AUTHENTICATION_FAILED`, counted |
| Algorithm does not match the key type of the peer's certificate | `AUTHENTICATION_FAILED` |
| Signing fails in OpenSSL | as in 47688: responder answers `AUTHENTICATION_FAILED`, initiator drops the SA |
| Peer uses a hash this side did not announce | `AUTHENTICATION_FAILED` |

No path continues with an empty or partial AUTH payload. Each rejection has
an error counter.

## Test plan

The test peer in `test/test_ikev2.py` gains method 14 for RSA-PSS and ECDSA.

- Regression: method 14 as initiator and as responder with an RSA key, the
  same with an ECDSA P-256 key; different hashes in the two directions.
- Profile matrix: `rsa-sig` and `digital-signature`, each with and without
  the notify from the peer, in both roles.
- Method 1 with a SHA-256 signature from the peer is accepted.
- Negative, at the input boundary: length octet 0, length octet larger than
  the payload, truncated `AlgorithmIdentifier`, SHA-1 identifier, RSASSA-PSS
  with default parameters, RSA algorithm with an ECDSA certificate, valid
  identifier with a signature made by another key, method 14 without a
  preceding notify, notify with an odd length, notify listing only SHA-1.
- A profile with a shared key sends no notify.
- The complete module runs with the default crypto policy of the toolchain
  container, where SHA-1 signatures are forbidden: the method 14 tests must
  pass there without the override that the method 1 test needs.
- Interoperability with a second implementation, both roles, RSA and ECDSA.

## Compatibility

- An `rsa-sig` profile against a peer without RFC 7427 behaves as today:
  no notify comes back, method 1 is used.
- An `rsa-sig` profile against a peer with RFC 7427 changes: both ends now
  use method 14 with SHA-2. This is the behaviour RFC 7427 §3 requires once
  the notify is exchanged, and what the plugin has been announcing.
- A responder that today receives method 14 from such a peer fails the
  exchange; whether that happens in practice is what step 1 measures.
- Removing the notify from an IKE_SA_INIT message in transit does not force
  method 1 silently: each side signs its own IKE_SA_INIT message as sent
  (RFC 7296 §2.15), so the altered message fails authentication. A site
  that must never fall back uses `digital-signature`.
- The API change is additive: one new enumeration value.

## Out of scope

- Certificate chains, Certificate Request payloads and revocation: the
  plugin compares against one configured certificate and keeps doing so.
- More than one local private key. Selecting between an RSA and an ECDSA
  key per profile (RFC 7427 §5) needs that and is a separate proposal.
- EdDSA (RFC 8420) and the fixed-curve ECDSA methods 9, 10 and 11, which
  RFC 8247 §3.1 expects to be replaced by method 14.
- Removing method 1.

## Implementation status, 2026-11-12

Steps 2 and 3 exist for RSA keys on a branch based on 47688, 47691 and 47698.
`test_ikev2` passes 68 of 68, including cases for each row of the failure
table. Against strongSwan 6.1.0 the exchange completes in both roles under a
crypto policy that forbids SHA-1 signatures: the peer verifies
`RSA_EMSA_PSS_SHA2_256_SALT_32` from VPP, and VPP verifies the peer's
`sha256WithRSAEncryption`. Not done: ECDSA keys, RSASSA-PSS with SHA-384 and
SHA-512, step 4.

