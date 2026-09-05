# `CB3InputManager` — input subsystem entry point

**Status: no reimplementation needed.** Confirmed by reading [shipa-2/Burnout3Recomp](https://github.com/shipa-2/Burnout3Recomp)'s `hle_xinput.cpp`: every Xbox kernel function this subsystem depends on (`XGetDeviceChanges`, `XInputOpen`, `XInputClose`, `XInputGetState`) is already HLE'd there, mapping real host XInput (plus a keyboard fallback — WASD/arrows) into the original Xbox `XINPUT_GAMEPAD` layout. `CB3InputManager::Update` itself is genuine recompiled game code (not hand-hooked) sitting on top of that kernel layer, so it should just work once the loading-screen hang (separate issue) is past. Nothing to write here — this subsystem turned out to be "already done" rather than "next to reimplement." Kept below as the reverse-engineering record.

The section below (entry point, structure) was written against the earlier reburn3/Cxbx-Reloaded plan, before this project switched base — still accurate, just no longer pointing at unstarted work.

## `CB3InputManager::Update` — `0x00021a50`

Name recovered via [Burnout3Recomp](https://github.com/mxmstr/Burnout3Recomp) (see
[README Credits](../../README.md#credits)); role confirmed by independent decompilation here.

Callers: `0x0002f650` (once), `0x000165f0` (three call sites — likely per-frame update plus one or
two special-case paths, not yet distinguished).

### What it does

Manages a fixed array of **4 controller port slots** (matches the original Xbox's 4 physical
controller ports):

```c
void CB3InputManager__Update(void)
{
    FUN_001b57e0(this);              // refresh device enumeration (likely wraps XGetDeviceChanges)

    // pass 1: for each of the 4 ports with a bound handler object, call vtable+4 (poll?)
    for (each of 4 slots) {
        if (slot.handler != null)
            slot.handler->vtable[1]();  // +4
    }

    // pass 2: for each of the 4 ports, check connection-state transition
    for (each of 4 slots) {
        state = slot.connectionState;   // -1 = not connected
        if (state == -1) {
            if (thisIsConnected && slotWasConnected) {
                bind slot;
                activeCount++;
                slot.handler->vtable[3]();  // +0xc -- likely "OnConnect"/bind handler
            }
        } else if (thisIsNotConnected) {
            slot.handler->vtable[4]();      // +0x10 -- likely "OnDisconnect"/unbind handler
            slot.slotArray[state] = 0;
            activeCount--;
        }
    }

    FUN_00018170();                  // unidentified, called once at the end -- possibly a global sync/flush
}
```

(Pseudocode above is a cleaned-up paraphrase of the Ghidra decompilation for readability; see the
raw output by re-running `tools/ghidra-xbe` against `0x00021a50` if you need the literal pointer
arithmetic.)

### Open questions before reimplementing

- `FUN_001b57e0` (called first, unconditionally) — not yet identified. Likely wraps the Xbox kernel's
  `XGetDeviceChanges`/`XInputOpen` device-enumeration refresh (consistent with the `[HLE] XGetDeviceChanges`
  / `[HLE] XInputOpen` log lines observed independently — see [prototype-leaks.md](prototype-leaks.md)
  methodology notes for how cross-referencing other builds/tools helps here).
- The vtable layout of the per-port handler object (`+4` = poll, `+0xc` = connect, `+0x10` =
  disconnect, by call-site inference) isn't independently confirmed against RenderWare or Xapi
  headers yet — this is read off call-site *shape*, not a known interface.
- `FUN_00018170` (end of function, unconditional) — not yet identified.
- Three separate call sites in `0x000165f0` haven't been distinguished (main loop vs. menu-only vs.
  pause-state, or simply redundant).

### Plan for reimplementation

Same pattern as [graphics-manager.md](graphics-manager.md): once the per-port handler vtable slots
are confirmed (ideally via a live breakpoint on entry to `0x00021a50` while plugging/unplugging a
controller, watching which vtable slot fires), replace the body with a call into real
`XInputGetState`/`XInputGetCapabilities` (modern Windows XInput, distinct from the Xbox kernel's
own same-named API already auto-identified at `0x00363c86` etc. — see `docs/functions.csv`),
translating state into whatever the existing per-port objects expect, then hook via `inject.cpp`'s
`WriteJmpRet` pattern. Not started — this note exists to make the actual coding a scoped, bounded
task for whoever (or whichever future session) picks it up next, rather than starting from zero.
