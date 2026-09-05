# Using earlier development builds as a research aid

Findings derived by comparing `default.xbe` against other development builds of the same title
(addresses, code structure, cross-references) can be documented here like any other finding.
**What doesn't go in this repo: the files themselves, or anything identifying which specific
build(s), where they came from, or how they were obtained.** Cite findings as coming from "an
earlier development build" without naming it.

## Why this is useful at all

Reverse-engineering a stripped retail binary is strictly harder than it needs to be when earlier
builds of the *same* codebase exist:

- **A build sharing retail's title ID** is, functionally, an earlier snapshot of the same source
  tree. Its compiled functions match retail's closely enough that a binary diff (Ghidra Version
  Tracking, BinDiff, Diaphora, or similar) can carry a match from one build to the other — even
  without any symbols, just from code shape and call-graph position.
- **Debug/dev builds are typically far less stripped than a retail master.** Assert strings, debug
  print statements, and less aggressive optimization all lower the cost of understanding what a
  function does, even when no formal debug symbol file accompanies the build.
- **A build that behaves *differently* from retail at a specific point** (see
  [disc-check.md](disc-check.md)) is itself a diagnostic signal: if the surrounding code is
  otherwise identical, whatever differs between the two builds' behavior narrows down where the
  actual cause lives, independent of what either build's code happens to be named.
- **A build for a different but closely related platform** (e.g. a PS2 build of the same title) is
  much less directly useful for x86/Xbox-specific reverse-engineering — different ISA, different
  compiled code entirely — but can still inform understanding of game-level logic, structure, or
  tuning that isn't tied to a specific CPU architecture.

## Working rule for this project

Concrete findings (addresses, decompiled logic, which functions correspond to which across builds)
are fair game to document, same as any other finding in this repo. Two things stay out: the build
files themselves, and any statement of provenance (filenames, version labels, where/how obtained).
When citing something found this way, say "an earlier development build" and nothing more specific.
