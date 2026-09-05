# A PS2 development build's linker map — full, unmangled C++ symbols

Per [prototype-leaks.md](prototype-leaks.md): specifics of where this build came from aren't
recorded here, only the finding itself. This is an earlier development build of **Burnout 3
itself** on **PlayStation 2** (mid-2004, roughly contemporaneous with the Xbox retail build's own
development) — a different CPU architecture (MIPS R5900 vs. Xbox's x86), so none of it is directly
usable for binary-level or structural cross-reference the way the [Burnout 2 debug
build](burnout2-source-tree-map.md) is. What it *does* carry is something even better for naming
purposes: **linker MAP files with fully-qualified, unmangled C++ symbols** — namespace, class,
method name and (truncated) argument types, straight from the CodeWarrior/MetroWerks PS2 toolchain
that shipped this build.

## What was on the disc

Three MetroWerks-style binary linker MAP files (`~2.5–3.2 MB` each), each covering a slightly
different link configuration of the same build (a full-debug link, an "internal" link, and an
unoptimized/`-O0` link) — the same source tree, linked three times with different settings. A
fourth, much smaller MAP file (for a bundled network middleware library) uses an unrelated ASCII
format and wasn't parsed.

## Format

Not a text map — each symbol is a fixed-header binary record: a 4-byte little-endian address, a
4-byte little-endian size, then a name string and a `(source file)` string, tab-separated and
null-terminated, with the whole record padded out to the next entry with runs of `0xCD` filler
bytes. Parsed all three MAP files by splitting on `\xcd{8,}` runs and pulling the two
tab-separated strings out of what's left between them.

Critically, unlike the Xbox retail binary (or even the Burnout 2 *debug* build, which only exposes
source *file* paths via `GTASSERT` strings), **this toolchain's linker map stores the actual
demangled C++ signature as the symbol name** — e.g.
`CB3EffectsManager::SpawnParticlesFromPoint(GtMathPs2::CGtV3d,GtMathPs2::CGtV3d,GtMathPs2::CGtV3d,...)`
— no demangling step needed, just string extraction. (Argument lists get truncated past a fixed
column width in the original record, so most signatures cut off mid-argument-list — harmless, since
the class and method name are always intact before the truncation point.)

## What's actually in it

Of ~14,400 raw symbol records across the three files, the overwhelming majority are RenderWare,
PS2 kernel/IOP, DirtySock (network), and libc/libm symbols — stock middleware, not game code (same
situation as the Xbox binary's XbSymbolDatabase-identified library functions). After filtering down
to symbols with a `Class::method` shape and deduplicating across the three MAP files: **115 unique
(class, method, source file) triples, covering 67 distinct classes across ~50 source files.**

Full table: [research/data/ps2-build-symbols.csv](../data/ps2-build-symbols.csv).

## Confirms the naming convention, at the *right* game generation this time

Every one of the 67 classes uses the `CB3*` / `CGt*` convention already established from the Xbox
binary and the Burnout 2 cross-reference — but this time it's not "one game earlier and probably
close enough," it's **the literal same title, same source tree, same era of development**. That's
strictly stronger evidence than the Burnout 2 correspondence for the classes it covers.

## Where it overlaps (or doesn't) with what's already documented

**No overlap** with the six classes already named from the Burnout 2 cross-reference
(`CB3AsyncDataLoader`, `CB3InputManager`, `CB3GraphicsManager`, `CB3DebugManager`, `CB3Game`,
`CGtFSM`) — this PS2 map happens to cover a completely different slice of the codebase:

| Area | Classes found |
|---|---|
| Vehicle AI / traffic | `CB3AIAvoidanceMap`, `CB3AITarget`, `CB3AITargetSpline`, `CB3TrafficSystem` |
| Vehicle physics / collision | `CB3CollidingBody`, `CB3ConvexHullCollide`, `CB3VehicleDeform`, `CB3HingedPart`, `CB3ClusterRig` |
| Camera | `CB3CameraUtils`, `CGtCameraFrustum`, `CGtCameraFrustumBase`, `CGtFrustumBuilder` |
| Rendering effects | `CB3EffectsManager`, `CB3Bloom`, `CB3Fog`, `CB3ShadowRenderer`, `CB3TrackRenderer`, `CB3VehicleRenderer`, `CB3TrailSystem`, `CB3ScrapeSystem` |
| 2D UI / HUD | `CGt2dObjectTable`, `CGt2dObjectText`, `CGt2dObjectImage`, `CGt2dObjectItalicText`, `CGt2dBezierCurve`, `CGt2dObjectVignette`, `CGt2dObjectVideoImage`, `Gt2dRenderer`, `CB3HUDScore`, `CB3HUDBackground2dObject`, `CB3HUDPrimaryMessageHandler`, `CB3ScrollingText2dObject`, `CB3StylisedText2dObject`, `CB3GradientText2dObject`, `CB3BurningText2dObject`, `CB3FlashText2dObject`, `CB3TipText2dObject`, `CB3RotatingImage2dObject`, `CB3ImageReward2dObject`, `CB3ImageVignette2dObject`, `CB32dObjectGradient`, `CB32dObjectOffscreenImage`, `CB3Icon2dObject`, `CB3Score2dObject`, `CB3TableComponent`, `CB3TextComponent`, `C2dObjectBoostBar`, `C2dObjectBoostBarMessage`
| Frontend pages | `CB3ResultsPage`, `CB3RoadRageResultsPage`, `CB3OnlineLobbyPage`, `CB3OnScreenKeyboardComponent`, `CB3ScrollVSelectComponent`, `CB3VOptionsSelectComponentEntryData`, `CB3CarViewerGameMode`
| Race state / misc | `CB3RacePosition`, `CB3WrongWayWall`, `CB3SoundSkidModel`, `CB3NetworkRaceUpdateMessage`, `CBlit`
| Math / geometry (namespaced `GtMathPs2::`) | vector/matrix types, `GtIntersection`, `CGtUnicode`

## Limitation — this doesn't hand us Xbox addresses

None of this identifies *where* these classes' code lives in the Xbox `default.xbe` — different
architecture, different compiler, no shared binary layout. Using this requires the same manual
process as the Burnout 2 work: pick a class/method here, find its probable counterpart in the Xbox
decompilation by behavior/structure, and confirm before renaming. Not yet done for any of these 67
classes — this note only records that the material exists and what it covers.

## Next step

Cross-reference the highest-value targets first — `CB3EffectsManager` and the vehicle-AI/traffic
classes are prime candidates since Function Atlas already has decent-sized unnamed clusters in
`game_physics`/`game_vehicle`/categorized-but-unnamed buckets that could plausibly correspond.
