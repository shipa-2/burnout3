# Burnout 3: Takedown — Static Recompilation

> **The first known static recompilation of an original Xbox game into a native PC executable.**

This project takes the original Xbox binary of **Burnout 3: Takedown** (2004, Criterion Games / EA) — 2.73 MB of raw x86 machine code — and translates every function into native C code that compiles into a real executable. No emulation, no interpreter, no dynamic recompilation: 22,097 lifted functions running as compiled x86-64 code.

**Platform note:** the current build path (below) is MSVC/Windows, inherited from how this project started. This fork's own goal is a **native Linux binary** — not a Windows-specific project — so expect the build instructions here to change as that lands; treat "Windows 11" as today's reality, not the destination.

![Title intro video playing through the boot sequence](docs/screenshots/title.png)
![Intro video - racing footage from the original XMV videos](docs/screenshots/introvideo.png)
![Main menu with full Burnout 3 logo, all options, and scrolling chyron](docs/screenshots/menu_main.png)

## This fork

Independent reverse-engineering research on this exact retail binary lives in [`research/`](research/) — notes on specific subsystems, cross-references against sibling Burnout titles, and the history of how this project ended up as the active base (was: reburn3/Cxbx-Reloaded → mxmstr/Burnout3Recomp → here). Full account in [research/ROADMAP.md](research/ROADMAP.md). No upstream code is modified by this addition.

**[Function Atlas](https://shipa-2.github.io/burnout3/decomp-atlas/function-atlas.html)** — a treemap of all 8,308 functions Ghidra found in `default.xbe`, colored by how well each one is identified (stock library code / named game code / still unnamed). Generated from [`docs/decomp-atlas/functions.csv`](docs/decomp-atlas/functions.csv).

This repository has no stated license — fork/PR here, don't assume redistribution rights.

## Why this is interesting

Static recompilation has real precedent elsewhere — [N64: Recompiled](https://github.com/N64Recomp/N64Recomp) for MIPS→C, [XenonRecomp](https://github.com/hedge-dev/XenonRecomp) for Xbox 360's PowerPC (Sonic Unleashed, etc.) — but the **original Xbox** has been overlooked, its emulation scene relying entirely on dynamic recompilation (Cxbx-Reloaded, xemu). Nobody had attempted a full static recompilation of a retail OG Xbox game before this.

What makes it interesting technically: OG Xbox is x86, so source and target architecture are related (x86 → x86-64) — but that also means confronting all of x86's baggage (variable-length instructions, complex addressing modes, the flags register, the FPU stack, segment prefixes) that a cleaner RISC source ISA wouldn't have. The Xbox SDK also statically links 11 libraries into every game binary that have to be identified and handled before the game's own code can be told apart from Microsoft's.

## Current status

**Phase 5: Integration.** The game boots, loads all resources, transitions through its own state machine (loading → init → crash-mode state → menus/frontend), and renders the main menu with all UI elements via a live NV2A push buffer → D3D11 translation pipeline.

**Working:** full main menu rendering (32 draw calls/frame, real textures from `Global.txd`), boot video sequence (Criterion/EA logos, title intro via Media Foundation), the original RenderWare engine init and display driver pipeline, 37 tracks loaded with fly/drive camera, 67 vehicle models across 7 classes, AWD audio playback through a software mixer, MCPX APU audio emulation (adapted from xemu), Xbox texture unswizzle for non-DXT formats, VEH-based fault handling, keyboard + XInput gamepad input.

**Not yet working:** sub-menu navigation, NV2A register combiner emulation (hardcoded to MODULATE blend for now), RW scene traversal feeding the live push buffer pipeline, DirectSound → APU voice processor connection, vehicle paint-variant textures (`.btv`), full collision/physics world init, performance tuning.

## How it works

```
default.xbe → XBE parser → disassembler (function detection) → x86→C lifter → MSVC → native .exe
```
plus a runtime providing the Xbox kernel (147 imports → Win32), a D3D8→D3D11 translation layer, and a faithful reproduction of the Xbox's 64 MB memory layout. The register model, memory architecture, indirect-call dispatch, and D3D translation are documented in depth in [research/](research/) and the generic **[xboxrecomp](https://github.com/sp00nznet/xboxrecomp)** toolkit repo this project's tools live in.

## Documentation

Reverse-engineered file formats discovered during this work:

| Format | Description | Doc |
|---|---|---|
| BGV (`*.bgv`) | Vehicle geometry (vertices, normals, UVs, tri-strips) | [docs/formats/bgv.md](docs/formats/bgv.md) |
| `streamed.dat` | Track geometry sections | [docs/formats/streamed-dat.md](docs/formats/streamed-dat.md) |
| `static.dat` | Per-track DXT texture dictionary | [docs/formats/static-dat.md](docs/formats/static-dat.md) |
| `PrgData.bin` | Game config (nested pointer structure) | [docs/formats/prgdata.md](docs/formats/prgdata.md) |
| `Global.txd` | RenderWare texture dictionary | [docs/formats/global-txd.md](docs/formats/global-txd.md) |

Burnout-3-specific technical deep dives: [RenderWare engine](docs/technical/renderware.md), [track geometry pipeline](docs/technical/track-geometry.md), [vehicle model pipeline](docs/technical/vehicle-models.md), [game state machine](docs/technical/game-states.md).

## Target binary

| Field | Value |
|---|---|
| Developer / Publisher | Criterion Games / Electronic Arts |
| Platform | Xbox (original) |
| Engine | RenderWare (custom ~3.7 fork, statically linked) |
| Title ID | `0x4541005B` (EA-091) |
| XDK version | 5849 |
| Code size | 2.73 MB |
| Functions | 22,097 (20,816 auto-detected + manual entries) |
| Kernel imports | 147 |

## Building

Prerequisites right now: Windows, Visual Studio 2022 (MSVC), Python 3.10+, CMake 3.20+, and your own legally-owned `default.xbe` + game data.

```bash
py -3 -m tools.recomp "Burnout 3 Takedown/default.xbe" --all --split 1000   # generates ~4.4M lines of C, ~65s
cmake -S . -B build && cmake --build build --config Release
bin/burnout3.exe   # run from the repo root, game files under 'Burnout 3 Takedown/'
```

| Key | Action |
|---|---|
| WASD | Drive / fly camera |
| Tab | Sprint (fly mode) |
| T | Cycle tracks |
| F | Toggle fly/drive mode |
| M | 3D model viewer |
| N / P | Next / previous vehicle |
| F1 / F2 | Settings / debug menu |
| Gamepad | Left stick steer, RT/LT gas/brake, A/RB boost |

## Legal

Educational/preservation project. You need your own legitimate copy of Burnout 3: Takedown for Xbox — no original game assets are included here.

## References

[XBE format](https://xboxdevwiki.net/Xbe) · [Xbox kernel exports](https://xboxdevwiki.net/Kernel) · [RenderWare](https://gtamods.com/wiki/RenderWare) · [NV2A GPU](https://xboxdevwiki.net/NV2A) · [Xbox architecture](https://www.copetti.org/writings/consoles/xbox/)
