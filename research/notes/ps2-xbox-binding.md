# Binding PS2 names to Xbox addresses — methodology, results, and what doesn't work

Continuation of [ps2-build-symbols.md](ps2-build-symbols.md). That note validated the PS2
data source and found the address-correction technique (a per-function profiling stub this debug
build inlines, at a variable offset — usually `0xc0`–`0xd0` but not fixed). This note covers the
next step: growing the confirmed PS2 name list via call-graph crawling, and the attempts (successful
and not) to bind those names to specific unnamed Xbox addresses.

## Part 1: call-graph crawl — 113 PS2 methods across 44 classes, address-verified

**Method**: starting from a small set of already-cross-verified anchors
(`CB3AsyncDataLoader::Update`/`Construct`, `CB3Game::Construct`/`Prepare`), decompile each, extract
every `FUN_xxxxxxxx` call target, and for each one, try candidate address corrections (`-0xc0`,
`-0xd0`, `-0xb0`, etc.) against the linker map. A hit is trusted specifically *because* the address
was found as an actual call target inside a function this same process already confirmed — not
because of address arithmetic alone (see Part 2 for why arithmetic alone is unreliable). Each new
hit becomes a fresh seed, breadth-first, until a branch runs dry; independent seeds were added
periodically (`CB3RaceCar`, `CB3TrafficVehicle`, `CB3FrontEnd`, `CGtFSM`) to reach parts of the call
graph the original anchors don't touch.

**Tooling**: two Ghidra headless scripts, reusable for future sessions —
`BatchDecompile.java` (takes a text file of addresses, force-creates+decompiles each, one JVM
invocation instead of one per address) and `DecompileAt2.java` (single-address version, used for
side-by-side comparisons). Both live only in the scratchpad from this session; worth adding to the
repo's `research/tools/` if this work continues.

**Result**: 113 confirmed `(real PS2 address → Class::method)` pairs across 44 distinct classes.
Full table: [research/data/ps2-confirmed-callgraph.csv](../data/ps2-confirmed-callgraph.csv). New
classes beyond what was already known (`CB3AsyncDataLoader`, `CB3InputManager`, `CB3DebugManager`,
`CB3Game`, `CGtFSM`): `CB3AILane`, `CB3BehaviourOffset`, `CB3Bloom`, `CB3Burn`, `CB3ControllerMapping`,
`CB3CrashNavPage`, `CB3CrashReplayFrame`, `CB3EffectsManager`, `CB3FrontEnd`, `CB3GameData`,
`CB3GameMode`, `CB3GraphicsManager`, `CB3HardCodedCrashStageList`, `CB3MyBurnoutRecordsState`,
`CB3OnlineBuddiesMenuPage`, `CB3OnlineRecordsDisplayMenuPage`, `CB3Player`, `CB3Profile` (+
`CB3ProfileCalcuatedData`, `CB3ProfileManager`, `CB3ProfileStoredData`), `CB3ProgressionManager`,
`CB3RaceCar`, `CB3ReplayFrame`, `CB3ReplaySystem`, `CB3Score`, `CB3SoundCrashManager`,
`CB3TrafficParam`, `CB3TrafficSystem`, `CB3TrafficVehicle`, `CB3VehiclePhysics`, `CB3World`,
`CGtCollisionKDTree`, `CGtDictionary<T>`, `CGtInputDevicePS2DualShock2`, `CGtInputManagerPS2Pad2`,
`CGtLobbyPS2DirtySock`, `CGtNATDataManager`, `Gt2dRenderer`.

## Part 2: binding attempts against Xbox — what worked, what didn't

### Worked: shared-parent, same-position, independently pre-known

Decompiled `CB3Game::Update` on both platforms (PS2 real address `0x00131b60`, Xbox `0x000165f0`,
already named). The first two calls on **both** sides landed in the exact same order:
position 1 = `CB3DebugManager::UpdateStartOfFrame` (already named on Xbox from the Burnout 2
cross-reference), position 2 = `CB3AsyncDataLoader::Update` (this project's own earlier finding).
This is a nice third independent confirmation of both facts, but it doesn't produce a *new* name —
both were already known.

### Didn't work: position keeps aligning, then stops

Position 3 continues the pattern only on Xbox (`CB3MemoryManagerPS2::Update`, already named there
too). On PS2, position 3 is a different, unidentified call — checked its real address directly
against the map's `CB3MemoryManagerPS2::Update` entry and the gap is far too large (~10KB) to be
the profiling-stub offset. **Positional call order is not reliable past the first couple of calls**
— compilers inline different amounts on each platform, and even where they don't, subsystem update
order isn't guaranteed identical source-line-for-source-line between two separately-tuned platform
builds of the same game.

### Didn't work: cross-architecture constant search

Tried searching the Xbox binary for literal floating-point constants pulled from a PS2 function's
decompilation (`CB3RaceCar::UpdateAggressiveReaction`, values like `0xbe22f983`). Two ways: Ghidra's
own instruction-operand scalar search (found nothing — the values aren't literal instruction
immediates), and a raw byte search for the same 4-byte pattern in the Xbox XBE (also nothing).
Most likely explanation: what looks like a "constant" in MIPS decompiled output is frequently a
**PS2-local RAM address** (loaded via the standard MIPS `LUI`+`ORI` idiom for referencing global
data), not a portable tuning value — so it has no reason to appear anywhere in a different platform's
binary at all. This technique might still work for a function that genuinely embeds a game-design
tuning constant (not a pointer) inline, but distinguishing the two from decompiled output alone
isn't reliable without checking the underlying disassembly for `LUI`/`ORI` vs. an actual immediate
load.

## Where this leaves things

The 113-entry PS2 list is solid, reusable inventory — real class/method identities, address-verified,
independent of any Xbox correlation. Turning entries from it into new Function Atlas names requires
a per-function structural read (the same standard this project has held throughout: a match is only
as good as an actual behavioral comparison, not a coincidence of address arithmetic or call
position). Good next candidates given they're large enough to have a real fingerprint and cover
gameplay-central systems: `CB3TrafficVehicle::StartCrashing` (1148 bytes), `CB3RaceCar::Prepare`
(1544 bytes), `CB3AILane::UpdateCurrentAILaneSegment`.
