# Burnout 2's embedded source file list — a map for naming Burnout 3's subsystems

**This is the single most useful cross-reference finding so far.** A debug build of Burnout 2:
Point of Impact embeds full relative source file paths in its debug/assert strings (compiler debug
info wasn't stripped). This exposes the **entire source tree structure** of the Burnout engine one
game before Burnout 3 — 176 `.cpp` files, organized by subsystem.

Per [prototype-leaks.md](prototype-leaks.md): specifics of where this build came from aren't
recorded here, only the finding itself.

## Why this matters

Burnout 3 is one game later, same studio, same engine lineage. Even without exact symbol names for
most of Burnout 3's ~7187 still-unnamed functions, knowing the **category and probable file** a
Burnout-2-era equivalent lived in gives strong hints about what an unnamed cluster of functions in
Burnout 3 is likely doing — especially for functions we've already partially characterized by
*behavior* but not by name.

## Direct correspondences to what's already documented for Burnout 3

| Burnout 3 (this project) | Burnout 2 source file | Confidence |
|---|---|---|
| `CB3AsyncDataLoader::Update` / `::QueueLoadRequest` (`0x000110e0` / `0x00011240`, see [disc-check.md](disc-check.md)) | `Toolkits\CAsyncLoadManager.cpp` | High — name and role (async load queue) match closely |
| `CB3InputManager::Update` (`0x00021a50`, see [input-manager.md](input-manager.md)) | `Toolkits\CInput.cpp` | High — same role, same `Toolkits` category |
| `CB3GraphicsManager` (RenderWare init, see [graphics-manager.md](graphics-manager.md)) | `Toolkits\RwUtils.cpp` (RenderWare wrapper) + `Render\CRenderer.cpp` | Medium — likely split across both in B3, exact split unconfirmed |
| `CB3DebugManager__UpdateStartOfFrame` / `RenderPerfMonDataCallback` | `Game\CDebugManager.cpp` | High |
| `CB3FrontEnd_Construct` / `_Prepare` / `__Update` / `__Render` | `Game\CFrontEnd.cpp` | High |
| `CB3Game__Construct` | `Game\CGame.cpp` | High |

Note: Burnout 2's file names don't carry the `CB2`/`CB3` numeric prefix at the *file* level even
though the *class* names do carry it in the compiled binary (`CB2RIDV`, etc. — see
[sibling-games-survey.md](sibling-games-survey.md)). The prefix is applied to the class, not
necessarily the filename, in this era of the codebase.

## What "Toolkits" implies about `CGt`

[sibling-games-survey.md](sibling-games-survey.md) found no `CGt`-prefixed classes in Burnout 2 or
the original Burnout — `CGtFSM__GetStateFromID` etc. look Burnout-3-specific. But Burnout 2 already
has a **`Toolkits/` directory** — the *concept* of a shared, non-game-specific utility layer
(`CAsyncLoadManager`, `CInput`, `CForceFeedback`, `CMemoryCard`, `linearmalloc`, `RwUtils`) predates
the `CGt` naming convention by at least one title. Plausible reading: Burnout 3 renamed/reorganized
this `Toolkits/` layer under a `CGt`-prefixed naming scheme, keeping the same conceptual split
between "engine plumbing" and "game logic" that Burnout 2 already had.

## Full file list (176 files, by category)

```
Game/            21 files — game modes, progression, HUD-adjacent logic, value database/tuning
HUD/             20 files — one file per HUD component (health, speedo, crash score, etc.)
Menu/            37 files — menu pages and their graphics components
Networking/       5 files — Xbox Live (CXBOnline*)
Physics/          5 files — vehicle/traffic physics
Race/            32 files — AI drivers, traffic system, race state, replay
Render/          21 files — camera, particles, weather effects, RW pipeline wrappers
Sound/           12 files — engine/crash/traffic sound, music
Toolkits/         6 files — CAsyncLoadManager, CForceFeedback, CInput, CMemoryCard,
                            linearmalloc, RwUtils
main_xbx.cpp       1 file — entry point
```

Full list with exact filenames: see the `strings` output this was extracted from, or re-derive with:
```bash
strings -a <debug-xbe> | grep -E 'gamesource.*\.cpp$' | sed 's|.*gamesource\\\\||' | sort -u
```

## Confirmed: `CAsyncLoadManager` in Burnout 2 == `CB3AsyncDataLoader` in Burnout 3 — near-identical code

Ran Ghidra on the debug build, found which functions reference the `CAsyncLoadManager.cpp` string
(assert messages embed the source file), decompiled them, and compared directly against the retail
Burnout 3 decompilation already on record in [disc-check.md](disc-check.md):

**Burnout 2** (`FUN_0014ee20`, referenced from `CAsyncLoadManager.cpp`):
```c
if (*(int *)(param_1 + 0x4c + *(int *)(param_1 + 0x84c) * 0x58) != 0) {
    if (*(int *)(param_1 + 0x840) == 0) {
        ...
        uVar2 = FUN_00156140(param_1 + *(int *)(param_1 + 0x84c) * 0x58, 0x11);
        *(undefined4 *)(param_1 + 0x840) = uVar2;
        ...
    } else {
        iVar1 = (**(code **)(**(int **)(param_1 + 0x840) + 0x1c))();
        if (iVar1 != 2) { ... }
    }
}
```

**Burnout 3** (`0x000110e0`, `CB3AsyncDataLoader::Update`, retail):
```c
iVar1 = *(int *)(unaff_EDI + 0x788) * 0x50;
if (*(int *)(iVar1 + 0x4c + unaff_EDI) != 0) {
    if (*(int **)(unaff_EDI + 0x780) == (int *)0x0) {
        ...
        uVar2 = FUN_001b33a0(iVar1 + unaff_EDI, 0x11);
        *(undefined4 *)(unaff_EDI + 0x780) = uVar2;
        ...
    } else {
        iVar1 = (**(code **)(**(int **)(unaff_EDI + 0x780) + 0x1c))();
        if (iVar1 != 2) { ... }
    }
}
```

Same slot-check offset pattern (`+0x4c`), same vtable slot (`+0x1c`) for a status check against the
same value (`2`), same magic constant (`0x11`) passed to the "open/create" call. Struct layouts and
exact field offsets differ slightly (expected — a full field got added/reordered between titles:
Burnout 3's outer disc-check guard, see [disc-check.md](disc-check.md), doesn't appear to have a
Burnout-2-side equivalent in this exact function, so that part is new to B3, wrapping the same
inherited core loop), but this is unmistakably the *same algorithm*, barely touched between the two
games. `QueueLoadRequest`'s Burnout 2 counterpart (`FUN_0014e8b0`) matches just as closely — same
24-slot (`0x18`) ring buffer, same filename-length guard (64 chars), same generation counter.

## Implication for identifying the rest of Burnout 3

Given `Toolkits/CAsyncLoadManager.cpp` carried over this closely, it's reasonable to expect the rest
of `Toolkits/` (`CInput.cpp`, `RwUtils.cpp`, `CForceFeedback.cpp`, `CMemoryCard.cpp`,
`linearmalloc.cpp`) — and plausibly large parts of `Race/`, `Render/`, `Physics/` too — carried over
with similarly minimal changes. This makes Burnout 2's debug build a genuinely strong Rosetta stone
for Burnout 3's remaining ~7187 unnamed functions: find the Burnout-2-era equivalent by structure,
confirm the file it's assert-tagged with, then look for the same shape in Burnout 3.

Address-to-source-file mappings already extracted for a few files (from the xref search that found
the above):

| Source file | Burnout 2 function addresses |
|---|---|
| `CAsyncLoadManager.cpp` | `0014e8b0`, `0014ee20` |
| `CInput.cpp` | `0014ff00`, `0014ffe0`, `001500e0`, `00150600`, `002f9cb0` |
| `RwUtils.cpp` | `00153690`, `00153c30`, `00153d80`, `00153e30` |
| `CDebugManager.cpp` | `000165f0`, `000170d0`, `00018b00`, `00018c20`, `00018d60`, `001ef1c0` |
| `CFrontEnd.cpp` | `0001adc0`, `0001b1e0` |
| `CGame.cpp` | `0001b340`, `0001bbe0`, `0001bc20`, `000249c0`, `0005f860`, `00066190` |

(Method: search the debug XBE's memory for the literal source filename string, then find every
cross-reference to it and note which function contains the referencing instruction — `GTASSERT`
macros embed `__FILE__`, so any function with an assert check gets tagged with its own source file.
Only catches functions that actually call `GTASSERT`, so this list is a lower bound per file, not
exhaustive.)

## Full automated sweep

`research/tools/ghidra-xbe/scripts/BatchSourceFileXrefs.java` now performs the same xref procedure
for the complete 176-file inventory. It searches each basename, walks back to the start of its
embedded path (where the code reference points), then records each containing function. The emitted
evidence is [research/data/burnout2-source-file-xrefs.csv](../data/burnout2-source-file-xrefs.csv):
1,619 direct string-xref rows, representing 617 distinct function/source-file associations across
174 source files. `Race/CCheckpoint.cpp` and `Race/CReplay.cpp` have no direct `GTASSERT` xref in
this build, which is an expected lower-bound result rather than evidence that the files were absent.

Run it against an already-analyzed debug-build Ghidra project as follows:

```bash
analyzeHeadless <project_dir> <project_name> -process <debug_xbe> -noanalysis \
  -scriptPath research/tools/ghidra-xbe/scripts \
  -postScript BatchSourceFileXrefs.java <source-file-list.txt> <output.csv>
```

## Next step

Use the now-complete lower-bound address-to-source map to decompile the Burnout 3 side one subsystem
at a time, using the corresponding Burnout 2 function as a structural reference rather than starting
from raw disassembly.
