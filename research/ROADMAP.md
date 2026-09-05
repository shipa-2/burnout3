# Roadmap

This is a working plan, not a fixed spec — it gets updated as findings change it. The goal of writing it down: avoid rabbit holes by knowing in advance what "stuck" looks like for each track and what the fallback is, instead of discovering it mid-way.

> **Base switched (post Phase 3).** Everything below through Phase 3 was written and executed against reburn3/Cxbx-Reloaded. Phase 3's own resolution (the "disc check" turned out to be a missing-data setup issue) is what led to actually testing [mxmstr/Burnout3Recomp](https://github.com/mxmstr/Burnout3Recomp) — a real static recompiler for this exact binary, already producing a working native executable. That's now the active base, forked at [shipa-2/Burnout3Recomp](https://github.com/shipa-2/Burnout3Recomp). Phases 1-3 are kept as-is below (accurate history, and Phase 2's Ghidra/naming work is still directly useful); Phase 4 onward now targets the fork instead of reburn3.

## Phase 4+ (current): work directly in the Burnout3Recomp fork

Track B (reburn3 build/tooling) and the reburn3-specific parts of Phase 4/5 below are superseded —
kept for history, not being pursued further. Current plan:

1. **Fix the loading-screen hang** ([notes/burnout3recomp-loading-hang.md](notes/burnout3recomp-loading-hang.md)) — first real task in the fork, blocks getting past the intro splash at all. Leading hypothesis: `Kern_NtReadFile` is fully synchronous where `CB3AsyncDataLoader::Update` (`0x000110e0`, already documented in [notes/disc-check.md](notes/disc-check.md)) may expect an observable pending→complete transition. Needs a debug build with symbols (or targeted logging) to confirm — the release POC's stripped native exe defeated `winedbg`'s stack walker.
2. ~~`CB3InputManager`~~ ✅ **Confirmed already handled** — the fork's `hle_xinput.cpp` fully HLEs `XGetDeviceChanges`/`XInputOpen`/`XInputGetState` with real host XInput + keyboard fallback. `CB3InputManager::Update` (`0x00021a50`) is genuine recompiled game code sitting on top; nothing to write. See [notes/input-manager.md](notes/input-manager.md).
3. **Fill in `sub_XXXXXXXX` placeholders** — most of the ~7187 still-unidentified functions from Phase 2 already exist as correctly-recompiled (if unnamed) code in the fork's `Burnout3RecompLib/x86_func_mapping.cpp`; naming and verifying them is now mostly a documentation/QA task, not new reverse-engineering from scratch.

Same fallback principle as below: if a specific piece turns out to be a much bigger rabbit hole than expected, back out, document what was learned, and pick a smaller piece instead of pushing through blind.

---

## Historical: Phases 1-3 (reburn3/Cxbx-Reloaded base)

## Guiding principle: three independent tracks

The three tracks below don't block each other. If one stalls, work continues on the others instead of stopping entirely.

```
Track A: Static RE          Track B: reburn3 build/tooling      Track C: Runtime validation
(Ghidra, no emulator)        (compiles without a working game)   (needs Cxbx-Reloaded actually booting)
      |                              |                                    |
      v                              v                                    v
 always available            always available                    blocked until disc-check
                                                                    is resolved (see Phase 3)
```

## Phase 1 — Foundation (done)

- [x] Build `reburn3.exe` under MinGW on Linux (case-insensitive header shim, ignore stale MSVC paths).
- [x] Extract `default.xbe` from a legally-owned NA-region ISO, verify signature/size.
- [x] Set up Ghidra + `ghidra-xbe` loader + XbSymbolDatabase, run full auto-analysis (8308 functions, 638 auto-identified as MS XDK library code).
- [x] Independently confirm one address reburn3 already patches (`0x0003c8a0`) via Ghidra's own function-boundary detection.
- [x] Diagnose (not yet fixed) why the game doesn't boot past the disc-authenticity screen under reburn3's launch mode.

## Phase 2 — Track A: static identification (RenderWare, then game code)

**Goal:** turn as many of the 7670 unnamed functions into named, understood ones — without needing the game to run.

1. Generate a targeted signature database from `reburn3`'s vendored `thirdparty/rw/lib/d3d8/*.lib` (the *exact* RenderWare build linked into this game) — via Ghidra FunctionID/BSim, or a FLIRT-equivalent.
   - **Stuck condition:** if the `.lib` object files don't yield usable signatures (stripped, LTCG-mangled, or format Ghidra's tooling can't ingest).
   - **Fallback:** manually cross-reference decompiled pseudocode against RenderWare's public headers (`thirdparty/rw/include`) function-by-function — slower, but always works, and is what reburn3's own author is presumably already doing.
2. Apply the signature database, re-run analysis, measure how many more functions get named.
3. For what's left (should now be mostly Burnout 3's own game code): pick subsystems in order of *isolation*, not importance — see Phase 4 for sequencing rationale.
4. Every finding gets written up in `notes/` the same way as `graphics-manager.md` (address, role, dependencies, confidence level) — no undocumented "I figured it out in my head" progress.

**Definition of done for this phase:** not "100% named" (unrealistic) — done when there's a documented, named entry point for whichever subsystem is being worked on in Phase 4, sufficient to start writing a reimplementation.

## Phase 3 — Track C: unblock runtime validation ✅ done (root cause was different than expected)

Resolved — see [notes/disc-check.md](notes/disc-check.md). The "disc problem" screen was never a
disc-authenticity check; it was a genuine file-open failure because early testing only had
`default.xbe` in place, not the rest of the extracted disc data. With the full data present, the
game boots to the title screen under reburn3's existing `/load` launch mode — no ISO-mounting,
Dokany, or Windows dependency needed after all. `cxbxr-debugger.exe`'s File Watch feature (log
`FailedOpen` events) is what actually found it; kept as the go-to tool for this class of problem
going forward.

<details>
<summary>Original phase plan (kept for reference — superseded by the finding above)</summary>


**Goal:** get far enough into the actual game (past the disc-check) to validate hooks live, not just statically.

1. Get access to real Windows (dual-boot, spare machine, or a VM with driver-passthrough support) — Dokany is a kernel-mode driver, Wine is not expected to support it.
2. In `cxbx.exe` (GUI, not reburn3's `/load` path), mount the actual ISO via its XISO Mount feature, boot the game directly (no reburn3 involved yet) — isolates whether the fix is about ISO-mounting at all, before touching reburn3's own launch code.
   - **If this passes the disc-check:** confirms the diagnosis in `notes/disc-check.md`. Next step: figure out whether reburn3's `cxbxbinding.cpp` can be extended to launch via a mounted ISO instead of `/load <xbe>`, and send that upstream.
   - **If this *also* fails on real Windows with a mounted ISO:** the diagnosis is wrong — the check is about something else entirely (region, save data, a totally different protection). Re-open the investigation from scratch: get a kernel debug log via `cxbxr-debugger.exe` at the exact point the check fires, rather than guessing again.
3. **Stuck condition:** no access to real Windows / VM with driver support at all.
   **Fallback:** narrow down *where exactly* the check fires (immediately on boot vs. only when starting a race) using `cxbxr-debugger.exe` breakpoints even without fixing it — if it's late enough, some subsystem hooks (e.g. input on a menu) might still be validatable before hitting it.

**Definition of done:** the game reaches actual gameplay (even briefly, even with graphical bugs) under some launch method, so a hook's *effect* can be observed, not just "it didn't crash."

</details>

## Phase 4 (historical) — Track A continued: pick and reimplement the next subsystem

Sequencing rationale: **easiest/most isolated first**, not most important first — this is what let reburn3's own author land the graphics manager entry point as a first success. Tentative order:

1. **Input manager** (matches the user's actual end goal — XInput) — **entry point identified**: `CB3InputManager::Update` at `0x00021a50`, see [notes/input-manager.md](notes/input-manager.md). Structure understood (4-port polling loop, per-port vtable dispatch for connect/disconnect); a few supporting functions (`FUN_001b57e0`, `FUN_00018170`) still unidentified. Reimplementation not started — this is the current active target.
2. **Audio manager** — DirectSound/XACT, similarly bounded in scope.
3. **UI/menu logic** — more central, touches more other systems.
4. **Physics/gameplay** — almost certainly the largest, most interdependent, last on purpose.

For whichever is picked: identify entry point in Ghidra (Phase 2 output) → write reimplementation (goes to reburn3 as a PR, not this repo — see README) → hook via `inject.cpp`'s `WriteJmpRet` pattern → validate live (Phase 3 is unblocked — see above).

**A major accelerant landed for Phase 2/4 both:** 480 of the ~7670 previously-unidentified functions now have real names, imported from [Burnout3Recomp](https://github.com/mxmstr/Burnout3Recomp) (see [README Credits](README.md#credits)) — a genuinely more advanced sibling project (true static x86 recompilation to a standalone native executable) that happens to have already solved function-boundary/naming for a large fraction of this exact binary. This project remains independent from it (own codebase, own goals, HLE-hook approach via reburn3) — only function *names* were imported, not code.

**Stuck condition:** a subsystem turns out to be far more entangled with unreimplemented code than expected (crashes elsewhere, depends on a dozen other fixed addresses).
**Fallback:** back out, document what was learned in `notes/`, and drop down to a smaller/more isolated piece of that subsystem instead of pushing through blind.

## Phase 5 (historical) — Track B: reburn3 upstream contribution (independent, can happen any time)

Already scoped in detail during planning; not repeated here. Concretely:
1. PR: MinGW build portability fixes (case-insensitive header shim, ignore/replace hardcoded MSVC paths) — codified in CMake, not just a local workaround.
2. PR: portable rewrite of the `ConstructLTCG` naked trampoline for GCC/MinGW.
3. Contact the maintainer (issue on GitHub) before anything bigger, given it's a single-author project with no public contribution process yet.

## When to revisit this roadmap

- After Phase 2 step 1 (signature generation) resolves one way or the other.
- After Phase 3 step 2 (real-Windows ISO mount test) resolves one way or the other.
- After the first subsystem in Phase 4 is fully done (reimplemented + validated) — recalibrate difficulty estimates for the next one based on how that one actually went.
