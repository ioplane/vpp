# Coding style

The fork adds no style of its own. Code follows upstream, because every change
is reviewed there. This page lists what upstream checks and where each rule is
defined, so a contributor can run the same checks before pushing.

## C

| Rule | Source in the tree |
|---|---|
| Formatting is `clang-format` with the repository `.clang-format` (GNU base, tabs) | `.clang-format` |
| Only lines changed by the commit are checked | `extras/scripts/checkstyle.sh` |
| No reformatting of untouched code in a functional change | review practice; keeps `git blame` useful |

Run before every push:

```bash
make checkstyle
```

## Python tests

Test code under `test/` is formatted with `black`; `make checkstyle` covers it.

## Commit message

Checked by `extras/scripts/check_commit_msg.sh`.

| Rule | Detail |
|---|---|
| Subject starts with a feature id from `MAINTAINERS` (`I:` lines) and a colon | `ikev2: reject inconsistent SA proposal length` |
| Subject at most 50 characters, body wrapped at 72 | `.git_commit_template.txt` |
| Body says what was wrong and what the change does | reviewers ask for it |
| `Type:` line with one of `feature fix refactor improvement style docs test make ci` | script constant `KNOWN_TYPES` |
| `Signed-off-by:` of the author | Developer Certificate of Origin |
| `Change-Id:` added by the Gerrit commit-msg hook | `docs/contributing/gitreview.rst` |
| No tool or assistant attribution lines | fork rule, see [rules.md](rules.md) |

## Error handling in new code

These are fork rules for code we write; they are stricter than upstream
requires and have not caused a review objection.

- A function that can fail returns a status its caller checks. It does not
  signal failure only by zeroed output or a sentinel value.
- A length, offset or count taken from a packet, a netlink message or a file
  is checked against the bytes that remain before it is used. Malformed input
  is rejected, not clamped or padded.
- A failure path releases what the function acquired, in reverse order,
  through one cleanup label.
- Each new failure branch has a test that drives it.
