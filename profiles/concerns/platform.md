# Concern: platform and low-level correctness

Taxonomy domain **S** (platform-specific and low-level correctness), plus the toolchain half of
**X8**. Rules in the `PLAT-*` namespace.

Enable with `"concerns": ["platform"]`. Checked by `sdlc-code-reviewer`.

For anything that runs somewhere other than the machine it was written on — which, once there
is CI, is everything.

## Assumptions about the host

- Path separators, case sensitivity, maximum path length, permitted filename characters. A test
  that passes on macOS and fails on Linux is usually a case-sensitivity assumption, and the
  reverse is usually a path-length one.
- Line endings on anything written, read or compared.
- A temporary directory is obtained from the platform, never hardcoded to `/tmp`.
- File permissions, symlink behaviour and atomic rename differ across filesystems. A
  write-then-rename that is atomic on one is not on all.
- Environment variables: name the ones required, their defaults, and the behaviour when absent
  or malformed at startup. Failing at first use instead of at startup turns a configuration
  error into a 3am page.

## Numbers and encoding

- Integer overflow, underflow and precision loss, especially before an allocation or an index.
  Say whether the language wraps, traps or is undefined here — the three behave differently
  and the code usually assumes one.
- Signed/unsigned conversions and narrowing casts.
- Endianness and alignment on anything serialised, memory-mapped or sent over a wire.
- Text is bytes until it is decoded. State the encoding; do not index into a UTF-8 string by
  byte offset and call it a character.

## Locale and time

- Case conversion, sorting, number and date formatting are locale-dependent. `toUpperCase` on a
  Turkish locale is the classic. Use an invariant locale for anything the program compares.
- The system clock moves backwards. A duration measured with a wall clock is not a duration;
  use a monotonic one.

## Process and toolchain

- Signal handling and shutdown: what happens to in-flight work on SIGTERM?
- Exit codes mean something to whatever invoked you.
- Resource limits — open file descriptors, process count — are real and are lower in a
  container than on a laptop.
- The toolchain is pinned where the project can pin it. A build that depends on whatever
  version is installed will differ between a developer's machine and CI, and `ENV-TOOLCHAIN-DRIFT`
  exists to say so. Native dependencies and cross-architecture builds are where this bites.

## The tool beats the opinion

A CI matrix across the operating systems and architectures you claim to support is worth more
than this entire file. `cross`, `cibuildwheel`, QEMU runners, `shellcheck` for portable shell,
and a 32-bit or big-endian target if you claim one.
