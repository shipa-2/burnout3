# `CB3GraphicsManager` — graphics subsystem entry point

**Status:** one function independently confirmed; reimplementation exists upstream in reburn3 (not duplicated here, see [Relationship to reburn3](../../README.md#relationship-to-reburn3)).

## `CB3GraphicsManager::ConstructLTCG` — `0x0003c8a0`

Confirmed via two independent methods:

1. **reburn3's own hook** ([`src/game/cb3graphicsmanager.cpp`](https://github.com/reburndev/reburn3/blob/master/src/game/cb3graphicsmanager.cpp), [`src/inject.cpp`](https://github.com/reburndev/reburn3/blob/master/src/inject.cpp)): patches this exact address to redirect into a reimplementation that calls real RenderWare (`RwEngineInit` / `RwEngineOpen` / `RwEngineStart`).
2. **Independent Ghidra analysis** (this repo, see [Tools](../../README.md#tools)): auto-analysis on a freshly imported `default.xbe`, with no hints from reburn3's code, resolves a function boundary starting exactly at `0x0003c8a0`. This corroborates that the address reburn3 patches is genuinely a function entry point, not a mid-function offset.

```
FUN_0003c8a0 @ 0003c8a0   (Ghidra auto-analysis, unnamed — not in XbSymbolDatabase,
                            as expected: this is RenderWare/game code, not an XDK library function)
```

### What it does (per reburn3's reimplementation)

A `__declspec(naked)` trampoline. The original compiler emitted a calling sequence where `this` arrives in `eax` at this address; the function moves it into `ecx` (thiscall convention) and jumps into `CB3GraphicsManager::Construct()`, which in turn calls into `RwEngineInit`/`RwEngineOpen`/`RwEngineStart` to bring up the RenderWare engine, and copies `RwMemoryFunctions` to the fixed address `0x007593d4` that not-yet-reimplemented original code still reads from directly.

### Why this matters for further work

- Confirms the general workflow (find address → cross-reference RW calls → reimplement → patch with a `WriteJmpRet` trampoline) is sound and independently verifiable via Ghidra.
- The fixed dependency on `0x007593d4` (`RwMemoryFunctions`) is a concrete example of the ABI constraint described in the README: as long as *any* original code path still reads that address directly, a reimplementation has to keep producing byte-compatible data there.
