# Binding PS2 names to Xbox addresses — methodology, results, and what doesn't work

Continuation of [ps2-build-symbols.md](ps2-build-symbols.md). That note validated the PS2
data source and found the address-correction technique (a per-function profiling stub this debug
build inlines, at a variable offset — usually `0xc0`–`0xd0` but not fixed). This note covers the
next step: growing the confirmed PS2 name list via call-graph crawling, and the attempts (successful
and not) to bind those names to specific unnamed Xbox addresses.

## Part 1: call-graph crawl — 770 PS2 methods across 246 classes, address-verified

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

**Result**: 366 confirmed `(real PS2 address → Class::method)` pairs across 233 distinct classes.
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

A later breadth-first pass used ten fresh seeds whose real entries were independently present in
Ghidra's function list after subtracting their observed profiling stubs (`0x90`–`0x100`). It added
`CB3AIDriver::CalculateSteerAngle`, `CB3NetworkCarPhysics::Update`,
`CB3StopJunction::Update`, `CB3EnvironmentManager::RenderBackdropTexture`,
`CB3MenuPageManager::Construct`, `CB3MenuFlowFSM::SetInitialMenuState`,
`CB3OnlineJoinGamePage::Prepare`, `CB3AIAggressionBehaviour::FindTarget`,
`CB3StageSelectState::Action`, `CB3MyBurnoutProfileLoadPage::SetMenuOptions`, and the outward
callee `CB3ImageVignette2dObject::_Render`. The crawl also reconfirmed
`CB3Bloom::SetRenderstates`, which was already present in the table.

The next pass added `CB3AIAvoidance::GenerateTarget`, `CB3RaceCar::SetFinished`,
`CB3Score::SetFinished`, `CB3SoundGameModeManager::Prepare`, `CB3SoundListener::Update`,
`CB3EndOfRaceState::AddRaceTimes`, `CB3OnlineSelNetConfigPage::Update`,
`CB3CrashCameraDirector::UpdateCrashMode`, `CB3OnlineRankingsState::Action`,
`CB3OnlineLobbySelectPage::Update`, `CB3OnlineGameCreateOptionsPage::Prepare`, and
`CB3RoadRageResultsPage::PrepareTable`. These ten seeds were again accepted only where the
map-minus-stub address was an independently existing Ghidra function entry; their two outward
callees extend the previously named `CB3RaceCar` and `CB3Score` classes.

A third UI/audio-oriented pass added `CB3BehaviourTrackSide::Prepare`,
`CB3SoundSkidModel::{Construct,Prepare}`, `CB3GlobeComponent::Update`,
`CB3AwardPresentationPage::PrepareTrackRecords`, `CB3ConnectionAnimationComponent::{Update,Construct}`,
`CB3SoundDistortion::CalculateGainPair`, `CB3StageLogic::UpdateCarDamage`,
`CB3EventFinishedState::Action`, `CB3HUDSoundManager::Construct`,
`CB3NetworkPlayer::BandwidthIsAvailableForCrashingTraffic`,
`CB3BoostEffectParams::GetRadialBlurParams`, and
`CB3OnlineGameCreateOptionsPage::{UpdateScroll,OnKeyboardCancel}`. The `Construct` callee for
`CB3ConnectionAnimationComponent` had no profiling stub: its call target itself equals the map
address and is an existing Ghidra function entry, so it is recorded with offset zero.

The fourth pass seeded sound, stage, streamed-track, online, and AI preparation routines. Its new
results include `CB3FrontEnd::SetInitialMenu`, `CB3Player::ResetLastInputTime`,
`CB3AIDriver::Prepare`, and `CB3BoostEffectParams::SetViewportEffects`, together with first
coverage for `CB3OnePlayerStage`, `CB3TwoPlayerSplitScreenStage`, `CB3AICar`, `CB3HUD`,
`CB3SoundScrape`, `CB3SoundESMHigh`, `CB3SoundESM`, `CB3SoundAICar`, `CB3StreamedTrack`,
`CB3OnlineConnectingPage`, and `CB3SatNavComponent`. Nine callees already in the table were
deliberately deduplicated; this pass contributes 18 new address/name pairs.

The fifth pass covered online/menu, crash, demo, static-track, and audio entry points. It added
`CB3Game::RequestNewGameMode`, `CB3ProfileInGameData::CacheCurrentProfile`,
`CGtSoundManager::StopAll`, and the state/action methods for `CB3DemoPauseState`,
`CB3DemoRaceResultsPage`, `CB3AwardPresentationState`, and `CB3PartyCrashSetupState`. It also
provides first method coverage for `CB3StaticTrack`, `CB3RaceFinishedPage`,
`CB3OnlineLoginToLobbyState`, `CB3CrashAnalyser`, `CB3OnlineOptimatchMenuPage`,
`CB3Button2dObject`, `CB3SoundDSPDataBlock`, and `CB3SparkRenderer`; 15 previously unseen
address/name pairs survived deduplication.

The sixth pass reached the online-lobby and SFIO callback branch. It adds three network-login
callbacks (`SFIOWriteCallback`, `SFIOOpenCallback`, and `SharedNetworkLoginSavePrepare`),
`CB3OnlineLobbyPage::OnKeyboardShow`, `CB3NetworkManager::ResetDNASStatus`, and both
`CB3OnlineStage` lifecycle methods. It also identifies `CB3GraphicsManagerBase` viewport/default
LOD setup, `Gt2dRenderer::EnableZTest`, `CB3MenuChoices::RequestMShowDemoGameMode`, and several
page/state helpers. This produced 21 fresh address/name pairs across 12 new classes; calls already
present in the table remained deduplicated.

The seventh pass added UI and state-machine coverage: `CB3PausePage`,
`CB3OnScreenKeyboardComponent`, `CB3TableComponent`, `CB3VOptionsSelectComponent`,
`CB3DNASPage`, `CB3CrashResultsPage`, `CB3OnlineCrashRecordsMenuPage`,
`CB3OnlineBuddiesState`, `CB3OfflineLapEliminatorLogic`, and
`CB3HUDPrimaryMessageHandler`. Its three immediate callees were already known, leaving 11 new
address/name pairs after deduplication.

The eighth pass added the crash/score/audio branch: `CB3CrashCombo::{OnCrashStart,ResetData,
UpdateCollidingPairs}`, `CB3FinishedScore::Prepare`, `CB3SoundCrashedTraffic::StartBassVoices`,
and `CB3SoundRaceCarManager::RequestRaceCar`. It also reaches `CB3PostEventPage`,
`CB3OfflineStageLogic`, `CB3OnlineTrackRecordsMenuPage`, and `CB3OnlineOpenLobbyPage`; the only
outward callee was `CB3Burn::Construct`. All 11 resulting addresses were previously absent.

The ninth pass added player/AI crash-state transitions (`CB3PlayerCar::StopCrashing`,
`CB3AICar::StopCrashing`, `CB3RaceCar::StopCrashing`, and `CB3AITarget` reset methods),
`CB3CrashScore` scoring helpers, controller look-back input, and UI/profile construction paths.
It contributes 17 new pairs across ten new classes after the known RaceCar, AICar, GameData, and
input-manager callees were excluded.

The tenth pass covered isolated menu and state-machine entry points. It records `CB3MainMenuState`,
`CB3DemoSelectState`, `CB3OnlineEndOfRaceState`, `CB3PlayerCameraStateEditor`,
`CB3StageSelectPage`, `CB3ScoreBonus`, `CB3OnlineGameOptionsPage`,
`CB3MemCardControllerBase`, and `CB3HeadingComponent`. No new mapped callee was reached, so this
pass contributes exactly its ten independently entry-point-verified seeds.

The twelfth pass added menu input, HUD score/impact-time, demo title, online connection/countdown,
replay-symbol, camera-editor, reward-image, and profile-records methods. These ten seeds produced no
new map-resolved callees but were independently verified as Ghidra function entries.

The eleventh pass covers `CB3TrafficValve`, online-lobby/upload/results state, progression and
championship helpers, `CB3SoundManager`, and two HUD components. Their decompilations did not
yield additional map-resolved callees; all ten entry-point-verified seed identities are retained.

The thirteenth pass adds settings/profile page preparation, demo-title state, scrape renderer,
buddy mail, offline crash replay, online crash results, and
`CB3OnlineTurnBasedCrashLogic::GetResultsPageType`. It contributes 11 new pairs; the discovered
`CB3MenuChoices` call was already present and was deduplicated.

The fourteenth pass added spark-array construction/preparation, race-position and checkpoint/start-
finish preparation, HUD/menu component setup, low-level sound release, VSelect item preparation,
and a second verified NAT unregister entry. One malformed seed address was caught before recording
and intentionally excluded.

The fifteenth pass covered online road-rage/comp-crash, aftermath, post-event rewards, network-car
sound preparation, AI arbitrator, countdown retrieval, wrong-way wall, track-material fixup, and
offline collision handling. It contributes 11 new pairs, including a second verified
`CB3MenuChoices` entry point.

The sixteenth pass adds race-position draw/prepare, traffic-lane fixup, track-material setup,
sound-skid volume calculation, camera-attrib registration/release, table-select preparation, and
network-replay retrieval. Nine fresh seeds were recorded; the duplicate online-results seed was
omitted.

The seventeenth pass adds traffic axle/lane helpers, inactive camera state, radial-blur and corona
array lifecycle, vehicle-reflectivity release, body-part construction, behaviour-interpolation
construction, online co-op crash preparation, and the hard-coded vehicle-name lookup. Ten seeds were
new; the two mapped callees were already recorded.

The eighteenth pass covers the vector/render-heavy remainder: HUD image construction, network crash
message retrieval, crash-action collision handling, spark frame setup, camera collision, shadow and
2D-object rendering, behaviour-cluster preparation, stylised results text, and aftermath state.
Twelve entry-point-verified pairs were added; these remain PS2 naming evidence and are not treated
as automatic Xbox bindings.

The twentieth pass added AI-target spline preparation, vehicle data fixup, fog CLUT generation,
behaviour-follow set-car, panel preparation, aftermath stepping, and vehicle-deform reset. Seven
seeds were retained. Two malformed addresses were rejected before recording after the check showed
they had been created by the batch script rather than independently present in Ghidra's function
list.

The seventy-eighth pass verified the unique CB3OnlineRoadRageRaceLogic::OnPostCrashReset() anchor and reached the radial-blur helper. One fresh entry were retained; shared-address road-rage signatures remain unassigned.

The seventy-seventh pass crawled four CGtInputDevicePS2DualShock deadzone, pause, connection, and construct methods and reached Gt2dRenderer::SetTextureAddressMode. Four fresh entries were retained after deduplication.

The seventy-sixth pass crawled five CB3AILane vector/segment helpers and reached the known forwards-vector and controller-pad helpers. Four fresh entries were retained; no Xbox names were inferred from vector-heavy bodies.

The seventy-fifth pass verified two CB3AITarget segment-state and release anchors. No additional named callees were reached; both addresses were retained.

The seventy-fourth pass verified three unique CB3OnePlayerStage render/update/construct anchors and reached HUD render, game-mode update, and simulation-pause helpers. Three fresh entries were retained after deduplication.

The seventy-third pass verified three unique CB3OnlineStage update/prepare/construct anchors and reached CB3GameMode::Construct(); ambiguous shared GetNumLaps/StartReplay address was excluded. Three fresh entries were retained.

The seventy-second pass crawled five CB3OnlineOptimatchMenuPage mode, table, release, sort, and network-game methods. No additional named callees were reached; all five anchors were independently verified.

The seventy-first pass crawled six CB3HardCodedCrashStageList lookup/region/prepare anchors (with one shared address kept as a single verified entry) and reached input/menu-choice helpers. Four fresh entries were retained after deduplication.

The seventieth pass crawled five CB3SoundAICar bass-voice, registration, prepare, construct, and destructor methods and reached HUD sound, sound-manager, and ESM-high helpers. Four fresh entries were retained after deduplication.

The sixty-ninth pass crawled seven CGtLobbyPS2DirtySock leave/join, persona, existence, and chat methods and reached game-search, bloom, menu-choice, and input helpers. Four fresh entries were retained after deduplication.

The sixty-eighth pass crawled two CGtVideoDecoder abort and MPEG callback methods. No additional named callees were reached; both anchors were independently verified.

The sixty-seventh pass crawled six CB3GraphicsManager vblank, viewport, render, RenderWare, prepare, and construct methods and reached video-mode and controller helpers. Three fresh entries were retained after deduplication.

The sixty-sixth pass crawled four CGtBuddiesPS2DirtySock invite, error, ban, and buddy-count methods and reached table/text/connection-animation, bloom, and graphics helpers. Four fresh entries were retained after deduplication.

The sixty-fifth pass crawled six CB3SatNavComponent junction, selector, outline, lead-in, animation, and construct methods. No additional named callees were reached; all six anchors were independently verified.

The sixty-fourth pass crawled six CGtSoundStream state, volume, media-buffer, update, and attach methods and reached CB3Bloom::SetRenderstates and CB3OnlineLobbyState::HandleInLobbyEvents. Three fresh entries were retained after deduplication.

The sixty-third pass crawled eight CB3AIAggressionBehaviour state, attack, horn, slam, and prepare methods and reached online-join, traffic-hull, and online-end-of-race helpers. Four fresh entries were retained after deduplication.

The sixty-second pass crawled eight CGtLobbyPS2DirtySock country, error, room, keepalive, player-count, search, and game-enumeration methods and reached bloom, online-crash, menu-FSM, and menu-choice helpers. Three fresh entries were retained after deduplication.

The sixty-first pass crawled five CB3ReplaySystem header, prepare, and lifecycle methods and reached the known online-buddies and vehicle-renderer helpers. Three fresh entries were retained after deduplication.

The sixtieth pass verified the final unique CB3AICar::CalcSeparationAlongTrack() anchor. One fresh entry was retained; its vector-heavy body was not used for Xbox naming.

The fifty-ninth pass verified the remaining unique CGtTimer Stop() and GetFrameCount() anchors. One fresh entry were retained; the other timer map address is shared by multiple signatures and was left ambiguous.

The fifty-eighth pass crawled eight CB3Profile totals, vehicle-usage, profile-name, and prepare methods and reached Evaluate/UnlockAll plus stored/calculated profile-data preparation. Three fresh entries were retained after deduplication.

The fifty-seventh pass crawled eight CB3Profile medal, crash-count, drift, oncoming, and slam-total methods. No additional named callees were reached; all eight anchors were independently verified.

The fifty-sixth pass crawled two CB3Player input/lifecycle methods and reached known controller/profile helpers. One fresh entry were retained after deduplication.

The fifty-fifth pass crawled five CB3DebugManager drawing and update methods and reached CB3BehaviourCluster::Interpolate. Four fresh entries were retained; no Xbox labels were inferred from vector-heavy debug rendering.

The fifty-fourth pass crawled the two remaining CB3HUDManager player-count and release methods. No additional named callees were reached; both anchors were independently verified.

The fifty-third pass crawled four CGtInputManagerPS2Pad2 port-binding, controls, device-ID, and prepare methods. No additional named callees were reached; all four anchors were independently verified.

The fifty-second pass crawled eight CB3VehicleDeform repair, residual, pivot, flying-bit, and roof/bumper methods and reached the known CB3BoostEffectParams radial-blur helper. Three fresh entries were retained; no Xbox labels were inferred from deformation-heavy code.

The fifty-first pass crawled four CB3MenuChoices request, selection, and prepare methods. No additional named callees were reached; all four anchors were independently verified.

The fiftieth pass crawled seven CGtNATDataManager registration, callback, entry, and port-mapping methods and reached the already-known SetUpAPortMapping helper. Three fresh entries were retained after deduplication.

The forty-ninth pass crawled five CB3TwoPlayerSplitScreenStage replay, lap, render, update, and construct methods and reached eleven named player, game-mode, graphics, FSM, HUD, and behavior helpers. Four fresh entries were retained after deduplication.

The forty-eighth pass crawled six CB3CrashCombo combo-state, pickup, style, update, and lifecycle methods. No additional named callees were reached; all six anchors were independently verified.

The forty-seventh pass crawled seven CB3MenuPageManager FSM, page-switch, and lifecycle methods and reached menu-choice, DVD-write, and chat-display helpers. Four fresh entries were retained after deduplication.

The forty-sixth pass crawled six CB3Score slam, boost, crash, grinding, and revenge methods and reached CB3Burn AddBurn/StopBurn. Four fresh entries were retained after deduplication.

The forty-fifth pass crawled seven CB3RacePosition rendering, lifecycle, and setup methods and reached CB3Score::IsAheadOfRoadRage. Four fresh entries were retained after deduplication.

The forty-fourth pass crawled eight CB3InputManager dead-input and menu-control methods. No additional named callees were reached; all eight anchors were independently verified.

The forty-third pass crawled the three remaining CB3ControllerMapping update/setup methods and reached Gt2dRenderer filtering plus two CGtInputManagerPS2Pad2 queries. Three fresh entries were retained after deduplication.

The forty-second pass crawled eight CB3SoundCrashManager impact and lifecycle methods and reached CB3ScrapeSystem::Release. Three fresh entries were retained; no Xbox labels were inferred from the vector-heavy bodies.

The forty-first pass verified the remaining CB3GameMode::Construct() anchor and reached the already-known CB3GameData::GetNumLaps() helper; one fresh address was retained.

The fortieth pass crawled four CB3StageLogic world, road-rage, damage, and fragility methods and reached ResetCarDamage. Three fresh entries were retained after deduplication.

The thirty-ninth pass crawled eight CB3OnlineLobbyPage image, car-class, NAT, page-mode, and chat methods and reached menu-choice, boost, and profile helpers. Four fresh entries were retained after deduplication.

The thirty-eighth pass crawled nine CB3OnlineBuddiesMenuPage callbacks and friend-list update methods and reached boost, spark-bank, input, allocator, and heading helpers. Four fresh entries were retained after deduplication.

The thirty-seventh pass crawled nine CB3AIAvoidanceMap traffic, no-go, crash, and update methods. No additional named callees were reached; all nine anchors were independently verified.

The thirty-sixth pass crawled seven CB3GameData threshold, lifecycle, and update methods and reached start/finish, split-checkpoint, offline-stage, stage-reset, and renderer callees. Four fresh entries were retained after deduplication.

The thirty-fifth pass crawled ten CGtLobbyPS2DirtySock callback, ranking, chat, and player-parameter methods and reached JoinLobbyCallback plus the input-device update. Four fresh entries were retained after deduplication.

The thirty-fourth pass crawled six CGtNetworkPlayerManager message and host-state methods. No additional named callees were reached; all six anchors were independently verified.

The thirty-third pass crawled nine CB3FrontEnd menu, video, audio, render, and update methods and reached seven named game-mode and online-page callees. Thirteen fresh entries were retained after deduplication.

The thirty-second pass crawled four CB3RaceCar crash and lifecycle methods and reached CB3AICar::Construct and CB3FinishedScore::Prepare. Three fresh entries were retained after address verification.

The thirty-first pass crawled ten CB3AILane segment and no-go queries and reached GetAvgForwardsVector through a verified lane-vector call. Four fresh entries were retained after address verification.

The thirtieth pass crawled ten CB3AITarget lane-selection and target-position methods and reached CB3AITargetSpline::IsSquareCorner. Four fresh entries were retained after address verification.

The twenty-ninth pass crawled ten CB3Profile timestamp, collection, trophy, and completion queries. No additional named callees were reached; all ten anchors were retained after verification.

The twenty-eighth pass crawled ten CB3AICar lifecycle and range-state methods and reached nineteen named callees; nineteen fresh entries were retained after address deduplication.

The twenty-seventh pass crawled ten CB3AIDriver speed, profile, drift, and update methods and reached CB3GameData::GetNumLaps and CB3AIArbitrator::CalculateCatchup. Twelve fresh addresses were retained after deduplication.

The twenty-sixth pass crawled ten CB3HUDSoundManager event and update methods. No additional named callees were reached; all ten seed addresses were independently verified.

The twenty-fifth pass crawled ten CB3Score state and event methods. No additional named callees were reached, but all ten anchor addresses were verified and retained for cross-architecture comparison.

The twenty-fourth pass crawled ten CB3Burn state/update methods and reached CB3Game::IsCrashMode through a verified call. Ten fresh addresses were retained after deduplication.

The twenty-third pass seeded CB3Game and CB3StageLogic lifecycle/state methods and found twelve additional named callees, including progression, async-loader, graphics, renderer, burn, and lobby callbacks.

The twenty-second pass seeded the controller-mapping input state machine and reached four CGtInputManagerPS2Pad2 methods through verified callees. Eight fresh controller anchors plus one newly discovered input method were added after address deduplication.

The twenty-first pass added profile locking, AICar range updates, GameData preparation,
GraphicsManager video/spheremap setup, network host keepalive, crash-sound preparation, VOptions
update, and CrashNav update. Nine new addresses survived deduplication; StopJunction and
EnvironmentManager calls were already present.

The nineteenth pass adds behavior-follow/keyframe/cluster updates, AI-target spline calculation,
camera replay cuts, race-car impulse, network crash retrieval, body-part and vehicle-deform helpers,
and HUD/engine sound lifecycle methods. Eleven vector-heavy but entry-point-verified pairs were
recorded for PS2 reference only.

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

An explicit check of the only same-name atlas candidate found so far, `CGtSoundManager::StopAll`,
was negative. The PS2 body loops over sound slots, clears per-slot fields, writes `0x41200000` and
`0x40800000`, then invokes one cleanup call; Xbox `0x001356a0` instead makes six unrelated-looking
subsystem calls and has no matching slot loop. The Xbox name remains its prior community label and
is not counted as a new cross-architecture confirmation.
