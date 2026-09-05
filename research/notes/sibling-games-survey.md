# Survey: other Criterion Games titles as cross-reference material

Goal: check whether other Criterion-developed Xbox titles share enough code/naming with Burnout 3
to help identify currently-unnamed functions in `default.xbe`, either via direct binary structure
(same architecture, close in time) or via naming-convention hints (even if not byte-identical).

Per [prototype-leaks.md](prototype-leaks.md): specifics of where these builds came from aren't
recorded here, only findings from studying them.

## What was checked

| Title | Year | Platform | Useful? |
|---|---|---|---|
| Burnout (original) | 2002 | Xbox (x86) | Limited — no `CB<N>`/`CGt` naming convention present yet |
| Burnout 2: Point of Impact | 2003 | Xbox (x86) | **Yes** — see below |
| Burnout 3: Takedown | 2004 | Xbox (x86) | (this project's own target) |
| Burnout 3: Takedown | 2004 | **PlayStation 2** (MIPS), dev build | **Yes, for naming only** — see below |
| Burnout Revenge | 2006 | **Xbox 360** (PowerPC) | Wrong architecture — see below |
| Black | 2005 | Xbox (x86) | No — different naming convention entirely, see below |
| Burnout Paradise | 2006 | Xbox 360 (PowerPC), pre-alpha | Not investigated further — wrong architecture, not checked |

## Findings

### Burnout 2: Point of Impact — useful

Confirms the `CB<N>` class-naming convention (`CB2RIDV`, `CB2...`) predates Burnout 3's `CB3*`
classes by at least one title — same numbering scheme, different game number, as expected.

A debug build (`b2_dxbox.xbe`, ~6.1 MB vs. the retail build's ~3.4 MB) has roughly **70% more
strings** than retail (40,036 vs. 23,557) and exposes plaintext gameplay-tuning identifiers
(`CAMERAFollowFOV`, `CAMERAELBOffsetY`, etc. — camera/physics tuning parameter names, likely from a
config/tuning system). No `CGt`-prefixed classes found here either — see below, `CGt` looks specific
to Burnout 3.

### Burnout 3: Takedown, PS2 development build — useful for naming, not for structure

Different CPU architecture (MIPS vs. Xbox's x86) rules out any binary-level cross-reference, but
this build's linker map stores fully-qualified, unmangled C++ symbols — no demangling needed.
Confirms `CB3*`/`CGt*` at the *same* game generation (not "one game earlier and probably similar"
like the Burnout 2 case). **4,588 methods across 672 classes**, address-verified against the actual
shipped executable (installing a proper PS2 Emotion-Engine Ghidra processor was needed to decompile
it reliably) and spot-confirmed structurally against the already-known `CB3AsyncDataLoader::Update`
— same ring buffer, same magic constant, three-way match with both Xbox builds. Full writeup:
[ps2-build-symbols.md](ps2-build-symbols.md).

**Not yet done:** a full Ghidra pass to see how much of this debug build's exposed naming
transfers conceptually to Burnout 3's own utility/shared code (same studio, one game apart in time,
plausible some low-level engine plumbing carried forward even without an exact `CGt`-style shared
library).

### Burnout Revenge (Xbox 360 beta) — real debug symbols, wrong architecture

This beta disc ships `B4Extern.pdb` (12.4 MB) + `B4Extern.pe` — genuine Microsoft PDB debug symbols.
**However:** `llvm-pdbutil dump --modules` shows `machine = powerpc 604` throughout, and the disc
itself ships `default.xex` (Xbox 360's executable format), not `default.xbe` — this is the **Xbox
360** version of Revenge, not original Xbox. Of 934 modules in the PDB, all but one are Microsoft's
own Xbox 360/Xenon SDK internals (`d:\xenon\nov05\core\private\xtl\...`); the one Criterion-authored
module reference is `CG4Game360\...\Burnout4_External.exp` (a linker export-definition artifact, not
compiled code).

**Verdict:** not directly usable for byte-level or even reliable structural cross-reference against
Burnout 3's x86 binary — different compiler, different ISA (PowerPC vs. x86), different codebase
generation for the 360 port. Might still hint at real subsystem names by analogy if the two
codebases share source-level naming (unverified, low confidence, not pursued further given the
architecture mismatch makes this a weak lead).

### Black — different naming convention, not a shared toolkit

Checked hoping `CGt`-prefixed classes (seen in Burnout 3 as `CGtFSM__GetStateFromID`) would appear
here too as evidence of a company-wide shared utility library. They don't. Black uses its own
distinct prefix (`CBkAI...`, `CBkRwAI...` — AI/pathfinding-specific: `CGotoAgent`, `CGraphManager`,
`CConstraintStealthPath`, etc.), pointing to a genuinely separate codebase/engine branch, not a
shared "CGt" toolkit reused across all Criterion titles regardless of genre.

## Conclusion

`CGt` appears to be specific to Burnout 3 (introduced sometime between Burnout 2's 2003 development
and Burnout 3's 2004 release), not a long-standing or cross-genre Criterion-wide toolkit. The
practical cross-reference value narrows to **the Burnout series specifically** (Burnout 2's debug
build being the most promising still-unexplored lead), not Criterion's catalogue broadly.
