# Resolved: "disc problem" screen was missing game data, not a disc check

**Status: RESOLVED.** Root cause had nothing to do with disc authenticity, security sectors, or
ISO-vs-loose-XBE launch mode — all of that was a red herring built on an incomplete test setup.
Kept below for the investigation trail, since the debugging path is itself useful reference.

## Actual root cause

`reburn3.exe`'s `/load <path-to-default.xbe>` only points Cxbx-Reloaded at the executable. It does
**not** imply the rest of the disc's contents (`Data/`, `Graphics/`, `Sound/`, `Tracks/`, `ovid/`,
...) are present anywhere reachable — those have to be extracted and placed alongside `default.xbe`
separately. Early testing in this project ran with only the bare XBE and no game data at all.

The game's own asynchronous read-status check (documented below, address `0x000110e0` /
`0x000214b0`) was doing exactly what it's supposed to do: reporting a **genuine file-open failure**
for a required asset — confirmed directly via `cxbxr-debugger.exe`'s File Watch feature (Breakpoints
tab → File Watch → Action: `FailedOpen`), which logs every failed file open in real time:

```
Opened file FAILED: "Sound\DSP\B3XboxFx.bin"
Opened file FAILED: "$u\contentmeta.xbx"
```

`Sound\DSP\B3XboxFx.bin` is a real, required asset (24,332 bytes on the actual disc) — it was
simply never extracted/placed next to `default.xbe`. (`$u\contentmeta.xbx` is unrelated — that's an
Xbox Live/profile content-metadata lookup that's expected to fail harmlessly with no save data
present.)

**Fix:** extract the full disc image (not just `default.xbe`) into the same directory
`reburn3.exe` points at. Once the actual game data is present, the check passes and the game boots
normally — no code patch of any kind was needed.

The byte patch described below (`0x10f8`: `JNZ`→`JMP`) is harmless dead-code-branch noise now that
the real cause is fixed, but it isn't necessary — reverting it doesn't reintroduce the problem, and
keeping it changes nothing observable. Left in place for now; worth reverting for cleanliness in the
eventual reburn3 PR.

---

## Investigation trail (kept for reference)

### Symptom

Launching the game via reburn3 (`reburn3.exe` → `cxbxr-ldr.exe /load default.xbe ...`) reached an
in-game screen reading:

> There is a problem with the disc you are using.
> It may be dirty or damaged.

This is rendered by the game itself (the string was not found anywhere in Cxbx-Reloaded's own
binaries — `cxbxr-ldr.exe`, `cxbxr-emu.dll` — meaning it's part of the game's own UI/asset data,
not an emulator error dialog).

### First (wrong) hypothesis: disc-authenticity/anti-piracy check

reburn3 always launches Cxbx-Reloaded with `/load <path-to-loose-xbe>`
([`src/cxbx/cxbxbinding.cpp`](https://github.com/reburndev/reburn3/blob/master/src/cxbx/cxbxbinding.cpp))
— Cxbx-Reloaded's HDD-emulation mode, not a mounted virtual DVD-ROM. `cxbx.exe`'s GUI separately
supports mounting a full `.iso` as a virtual DVD-ROM via Dokany. The initial theory was that some
in-game check specifically detects "not running from a real DVD" and shows this screen as a soft
anti-piracy measure.

Public Cxbx-Reloaded compatibility reports for this exact game
([issue #1077](https://github.com/Cxbx-Reloaded/game-compatibility/issues/1077),
[issue #375](https://github.com/Cxbx-Reloaded/game-compatibility/issues/375)) don't mention this
message — both get as far as menus/gameplay with graphical bugs instead, which in hindsight is
consistent with those testers having actually extracted full game data, unlike this project's
initial setup.

### The actual check, statically

The message is displayed by a function (retail: `0x000214b0`) that formats a localized string and
enters an unconditional draw loop — once entered, it never returns:

```c
if ((DAT_004aed9c != (int *)0x0) && (iVar1 = (**(code **)(*DAT_004aed9c + 4))(), iVar1 == 6)) {
    FUN_000214b0(DAT_004aed9c[2], 0);
}
```

(retail caller: `0x000110e0`). `DAT_004aed9c` is a pointer to some interface; the vtable call at
`+4` returns a status, and `6` triggers the error screen. An earlier development build sharing
retail's title ID (EA-091) has byte-for-byte identical logic at this point (caller/callee at
different addresses, same structure) — which was initially read as evidence *against* a disc check,
since that build booted fine even under the same loose-XBE launch mode. In hindsight this is exactly
consistent with the real explanation too: that build's data was available where it needed to be.

A byte patch (file offset `0x10f8` in `default.xbe`: `75`→`EB`, `JNZ`→`JMP`, making the call
permanently unreachable) was tested and did **not** fix the boot — correctly, since the actual
problem (missing files) was still there; the game would have failed differently once code past this
point tried to use the never-loaded DSP data.

An exhaustive scan of every instruction in `default.xbe` for any operand referencing
`0x004aed9c` found 12 references, all reads, no writes, no `LEA` — the pointer is a field of some
larger struct written via `[base+offset]` addressing, never traced to its assignment site. Static
analysis alone hit its ceiling here.

### What actually cracked it

`cxbxr-debugger.exe` (launched via `cxbx.exe`'s `Emulation → Start Debugger`, deprecated upstream
but still functional) has a **File Watch** feature completely separate from code/memory
breakpoints: Breakpoints tab → set `Filter` (e.g. `*`) and `Action` (`Opened` / `Read` / `Write` /
`Closed` / `FailedOpen`), and it logs matching file operations live in the Debug Output pane as the
game runs. Setting `Action: FailedOpen` immediately surfaced the real failing file open, which
static analysis (chasing the check's *logic*) was never going to find on its own — the check's
logic was correct all along.

## Practical impact on this project

Runtime validation of subsystem hooks is now unblocked — the game boots to the title screen with
the full extracted disc data present. `cxbxr-debugger.exe`'s File Watch is now a known-good tool for
catching file-level I/O problems quickly in future work, worth reaching for before falling back to
static disassembly reading.
