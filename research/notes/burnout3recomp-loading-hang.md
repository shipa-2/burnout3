# Observation: Burnout3Recomp loading-screen hang (not our bug to fix)

Not part of this project's scope — recorded here only because the diagnostic path used our own
understanding of `CB3AsyncDataLoader` (see [disc-check.md](disc-check.md)) and might save someone
time later.

While testing [Burnout3Recomp](https://github.com/mxmstr/Burnout3Recomp)'s proof-of-concept build
(see [README Credits](../../README.md#credits)), the game boots and renders at a stable 60 FPS but
never advances past an animated loading screen to the intro splash.

**Hypothesis, not confirmed:** `Kern_NtReadFile` in that project's `kernel/imports.cpp` implements
the read as fully synchronous — it performs the read and writes `STATUS_SUCCESS` into the
`IO_STATUS_BLOCK` immediately, in one call. If `CB3AsyncDataLoader::Update` (the same function
documented in this repo, retail address `0x000110e0`) or its callers expect to observe a
pending→complete *transition* (e.g. via a separate event/callback, not just a status value that's
already "done" the instant the call returns), a synchronous implementation could mean that
transition never visibly happens, and whatever polls for it never sees the condition it's waiting
for.

Not verified with a live debugger (their native recompiled executable has no debug symbols, and
`winedbg`'s stack walker couldn't unwind past `kernel32` without them). This is a plausible lead,
not a diagnosis.
