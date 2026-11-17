# RFC-0002: Nexthop objects in linux-cp

Status: draft, step 1 measured. Date: 2026-11-12, updated 2026-11-17. Roadmap: section 2.

## Summary

The Linux kernel can describe the next hops of a route as separate objects
that many routes share. linux-cp does not read these objects. It works today
only because the kernel, by default, repeats the expanded next hops inside
every route message. This proposal first proves the dependency with a test,
then teaches linux-cp to consume nexthop objects, so that route programming
stays correct when the compatibility mode is switched off and group changes
do not need one message per route.

## Normative references

- Kernel netlink specification `rt-nexthop`: operations `newnexthop`,
  `delnexthop`, `getnexthop`; attributes `id`, `group`, `group-type`,
  `blackhole`, `oif`, `gateway`, `encap-type`, `encap`, `res-group`.
- Kernel netlink specification `rt-route`: route attribute `nh-id`.
- Kernel `ip-sysctl`, `nexthop_compat_mode`: with the default `true`, "route
  dumps and notifications contain the new nexthop attribute but also the
  full, expanded nexthop definition"; resilient groups are then shown "as
  just a list of next hops" and "weights that do not fit into 8 bits will
  show incorrectly".

## Current behaviour

At upstream `242ab5bfe`, `src/plugins/linux-cp/lcp_router.c` builds FIB paths
from the per-route list with `rtnl_route_foreach_nexthop ()` and
`lcp_router_route_path_parse ()`. The plugin handles
`RTM_{NEW,DEL}{LINK,ADDR,NEIGH,ROUTE}` only; it has no handler for
`RTM_NEWNEXTHOP` and never reads the route `nh-id` attribute.

Consequences, to be confirmed by the first step below:

1. With `nexthop_compat_mode=0` a route that references a nexthop object
   arrives without expanded next hops and is installed without paths or
   dropped.
2. A change of a nexthop group reaches VPP as one route notification per
   route that uses it.
3. Resilient groups and weights above 255 are not represented faithfully.

## Step 1 results

Measured on 2026-11-16 and 2026-11-17 with a debug image, kernel 6.12 and
`ip nexthop` in the test namespace. The plugin code was not changed.

| Case | Kernel sends | FIB of the plugin |
|---|---|---|
| Route with `nhid`, single object or group, mode 1 | route message with `nh-id` and the expanded next hops | correct paths |
| Route with `nhid`, mode 0 | route message with `nh-id` only | no entry, no error |
| IPv4, object deleted | `RTM_DELNEXTHOP` only | route stays |
| IPv6, object deleted, mode 1 | `RTM_DELNEXTHOP`, then `RTM_DELROUTE` | route removed |
| Member leaves a group, IPv4 and IPv6 | `RTM_DELNEXTHOP` of the member, `RTM_NEWNEXTHOP` of the group | route keeps the path of the member |
| `ip nexthop replace` of a used object | `RTM_NEWNEXTHOP`, then a route message per route | correct paths |
| Link goes down | no message for its objects or their IPv4 routes | routes removed by the existing link-down flush |

Consequence 1 above is confirmed: with mode 0 the route is not installed.
Consequence 2 holds for a replaced object only; a member that leaves a group
produces no route message at all. Two cases were not listed and are defects
with the default mode: the IPv4 route of a deleted object stays, and a path
through a removed group member stays.

Change 47816 adds the test of mode 1. Change 47866 removes the IPv4 routes
of a deleted object: it joins the nexthop multicast group, records the
`nh-id` of an IPv4 route and acts on `RTM_DELNEXTHOP`. A record costs about
74 bytes for a route with one path, measured with 20 000 routes.

The remaining work of step 2 is the table of objects: it is needed for a
member that leaves a group and for mode 0.

## Proposed behaviour

Step 1 — measure. Add tests to `test/test_linux_cp.py` that create nexthop
objects and groups with `ip nexthop` in the test namespace, install routes
with `nhid`, and check the resulting FIB paths with the compatibility mode on
and off. This step changes no plugin code and decides whether the later steps
are needed as written.

Step 2 — consume nexthop objects.

- Join the nexthop multicast group and handle `RTM_NEWNEXTHOP` and
  `RTM_DELNEXTHOP`; request a nexthop dump before the route dump on start
  and on resynchronisation.
- Keep a table from nexthop id to a parsed description: a single next hop
  (gateway, interface, encapsulation, blackhole) or a group of member ids
  with weights.
- When a route carries `nh-id`, build its paths from the table instead of the
  expanded list. A route whose id is unknown is held until the nexthop
  arrives or the resynchronisation completes; it is not installed with
  guessed paths.
- When a nexthop or group changes, re-program the routes that use it.

Step 3 — only if step 2 shows a need: map a group to one shared FIB
path-list so that a group change is a single FIB update.

## Failure handling

- A nexthop message that fails validation (unknown family, oversized
  address attribute, member id that does not exist) is rejected and counted;
  the table keeps its previous entry.
- Deleting a nexthop that routes still reference removes those routes'
  paths in the same pass, as the kernel does, and is counted.
- Netlink overrun triggers the existing resynchronisation, extended to dump
  nexthops first.
- Table memory is bounded by the number of kernel nexthops; allocation
  failure aborts the update and leaves the previous state.

## Test plan

- Single nexthop, ECMP group, weighted group, group member replace, group
  delete while referenced, blackhole nexthop, IPv4 and IPv6, MPLS
  encapsulation on a nexthop.
- Each case with `nexthop_compat_mode` 1 and 0.
- Negative: route with unknown `nh-id`, group with an unknown member,
  oversized gateway attribute.
- Resynchronisation after a forced overrun with 10 000 routes on 16 groups.

## Compatibility

A kernel or routing daemon that does not use nexthop objects sends none, and
behaviour is unchanged. With compatibility mode on, the object path and the
expanded list describe the same paths; the object path is preferred when
`nh-id` is present.

## Open questions

1. Answered: the plugin parses these messages itself. The upstream builders
   have libnl 3.7.0; libnl parses nexthop objects from 3.8 and reports the
   `nh-id` of a route from 3.10.
2. Whether resilient groups should map to a VPP load-balance with a fixed
   bucket count or stay a plain weighted group.
3. Whether the plugin maintainers prefer step 3 from the start.

## Out of scope

Policy routing rules and VRF devices; they are separate roadmap items.
