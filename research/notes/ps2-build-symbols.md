# A PS2 development build's linker map — full, unmangled C++ symbols

Per [prototype-leaks.md](prototype-leaks.md): specifics of where this build came from aren't
recorded here, only the finding itself. This is an earlier development build of **Burnout 3
itself** on **PlayStation 2** (mid-2004, roughly contemporaneous with the Xbox retail build's own
development) — a different CPU architecture (MIPS R5900 "Emotion Engine" vs. Xbox's x86), so none
of it is directly usable for binary-level structural cross-reference the way the [Burnout 2 debug
build](burnout2-source-tree-map.md) is. What it *does* carry is something even better for naming
purposes: **a linker map with fully-qualified, unmangled C++ symbols** — namespace, class, method
name and argument types, straight from the CodeWarrior/MetroWerks PS2 toolchain that built it.

## Correction from an earlier version of this note

The disc actually ships **four** map files, and they are **not interchangeable** — each one
describes a different link of the codebase, with different (non-corresponding) addresses for the
same symbol:

| Map | What it's for |
|---|---|
| `B3DEBUG.MAP`, `B3INTERN.MAP`, `B3O0PCH.MAP` | Three other link configurations (full debug, "internal", unoptimized `-O0`) — **not** what's on this disc as a runnable executable. Binary-format (MetroWerks), addresses don't match the shipped ELF. |
| `DNAT_200.MAP` | The map for the executable this disc actually boots (`DNAT_200.45`, referenced from `SYSTEM.CNF`'s `BOOT2` line). Plain ASCII text, one `<address> <size> <section> <symbol>  (<source file>)` line per symbol. **This is the one with addresses that are actually decompilable and cross-checkable.** |

An earlier pass here parsed only the first three and got structurally-plausible-looking method
signatures, but decompiling at those addresses in the actual shipped ELF didn't correspond to
anything sensible — because those three maps don't describe that ELF at all. Re-parsing
`DNAT_200.MAP` instead fixed this: **4,588 method symbols across 672 classes**, all with addresses
that resolve to real, decompilable code in `DNAT_200.45`. Full table:
[research/data/ps2-build-symbols.csv](../data/ps2-build-symbols.csv) (columns: `address`, `size`,
`class`, `method_signature`, `source_file`).

## Tooling

- The disc is plain ISO9660 (not Xbox's XDVDFS) — extracted directly with `7z`.
- `DNAT_200.45` is a genuine MIPS III ELF (PS2 Emotion Engine). Ghidra's stock MIPS processor
  module doesn't understand the EE core's custom instruction extensions (MMI, VU0 macro mode) and
  produces badly-misaligned function boundaries as a result — installed
  [ghidra-emotionengine-reloaded](https://github.com/chaoticgd/ghidra-emotionengine-reloaded)
  (processor ID `r5900:LE:32:default`), which fixed disassembly and analysis quality substantially.

## Confirmed: methodology works, with one caveat

Cross-checked the two Xbox classes already named from the Burnout 2 debug-build correspondence
against this map, using their exact addresses this time (not guesswork):

**`CB3AsyncDataLoader::Update()`** (PS2 `0x0013a0a0`, decompiles cleanly) is a byte-for-byte
structural match to the already-documented Xbox retail decompilation
([disc-check.md](disc-check.md)): same `0x788`-offset ring-buffer index, same `* 0x50` per-slot
stride, same 24-slot (`0x18`) wraparound, and **the same magic constant `0x11`** passed to the
slot-open call. Three-way confirmation now: Xbox retail, Burnout 2's Xbox debug build, and this PS2
build all implement the identical algorithm.

**Caveat found while checking `CGtFSM::GetStateFromID`**: very small methods (this one is only 64
bytes in the map) don't decompile cleanly — this debug build's compiler appears to inline a
per-function profiling/instrumentation stub ahead of the real body, and Ghidra's function-boundary
detection merges several adjacent tiny methods (`StateEnter`, `StateLeave`, `GetStateFromID`,
`ApplyEvent`, `Update` — five separate map entries) into what looks like one large function
dominated by profiler bookkeeping code, with the actual per-method logic hard to isolate inside it.
**Substantial methods (roughly 300+ bytes) are reliable; small accessor/dispatch-sized methods are
not**, at least not without manually picking apart the instrumentation noise.

## What's in the corrected data

672 classes is far more than the 67 the earlier (wrong-address) pass found, and spans essentially
every subsystem: vehicle physics/collision (`CB3PhysicsManager`, `CB3VehicleDeform`,
`CB3ConvexHullCollide`), AI/traffic, rendering (`CB3GraphicsManagerBase`, `CB3TrackRenderer`,
`CB3EffectsManager`), sound (`CB3SoundScrape`, `CB3HUDSoundManager`), the full 2D UI/HUD/frontend
layer, and more. Direct hits already confirmed present for classes this project already knows by
name from Xbox: `CB3AsyncDataLoader`, `CB3InputManager`, `CB3DebugManager`, `CB3GraphicsManagerBase`
(Xbox has `CB3GraphicsManager` — worth checking whether Xbox's is actually the `Base` variant or a
sibling), `CGtFSM`.

## Not yet done

No *new* Xbox address has been named from this data yet — the one class checked in depth
(`CGtFSM::GetStateFromID`) was already named, and served only to validate the method and find the
small-function caveat above. Turning the other ~670 classes into actual Function Atlas entries
means the same manual, one-function-at-a-time process used for `CB3AsyncDataLoader`: decompile the
PS2 side (avoiding sub-~300-byte methods per the caveat), find a plausible Xbox candidate by
category/size/behavior, confirm with a real structural read, then name it. Worth doing, not worth
rushing — a wrong "confirmed" name is worse than an honest grey cell.

## Next step

Pick specific, substantial, distinctive-looking methods from
[the CSV](../data/ps2-build-symbols.csv) as targets — `CB3PhysicsManager` and `CB3VehicleDeform`
are good candidates given they're core, highly Burnout-specific systems with large (500+ byte)
methods throughout.
