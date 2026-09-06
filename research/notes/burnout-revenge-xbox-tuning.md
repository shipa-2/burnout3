# Burnout Revenge's original-Xbox demo build: a tuning-parameter tree, not source paths

Per [prototype-leaks.md](prototype-leaks.md): specifics of where this build came from aren't
recorded here. Notable purely because of *what* it is: a demo build of **Burnout Revenge**
(internally `B4` — one game after Burnout 3) for the **original Xbox**, not Xbox 360. The only other
Revenge material this project had previously seen was an Xbox 360 beta (wrong architecture — see
[sibling-games-survey.md](sibling-games-survey.md)), so this is the first Revenge material actually
worth cross-referencing against Burnout 3's own Xbox binary.

## What's actually in it

No `GTASSERT`/source-path strings, no symbol table — stripped the same way every other
non-debug build checked so far has been (see [prototype-builds-inventory.md](prototype-builds-inventory.md)).
What *does* survive, because it's needed at runtime for an in-game debug tuning menu even in a demo
build: **198 human-readable tuning-parameter category paths** — things like
`Physics/Race Car/Body Roll`, `Score/Boost/Boost Start`, `AI/Aggressive Driving/Slam`,
`Body Part Deformation/Glass Strengths`, `Crash Breakers/Type 9`. Full list:
[research/data/burnout-revenge-xbox-tuning-tree.txt](../data/burnout-revenge-xbox-tuning-tree.txt).

Top-level categories: `AI`, `Body Part Deformation`, `Camera`, `Crash`, `Crash Breakers`,
`FakePhysics`, `Modes`, `Physics`, `Rumble`, `Score`, `Sound`, `VehicleAudio`.

Checked whether Burnout 3's own retail binary has the same kind of strings — it doesn't. Burnout 3
only has ordinary file-path strings (`Data/GlobalIt.bin` etc.), no tuning-tree labels survive there.
So this isn't something to cross-reference byte-for-byte; it's **semantic corroboration** for
functions this project already has addresses for but doesn't fully understand:

| Already-known Burnout 3 function | Revenge category that lines up |
|---|---|
| `CB3RumbleAttribs__RegisterStaticVariables` (0x0001f7c0) | `Rumble/*` |
| `CB3AIAttribs__Register` (0x0016afd0) | `AI/*` |
| `CB3Score__RegisterStaticVariables` (0x00190430) | `Score/*` |
| `CB3Burn__RegisterStaticVariables` (0x0017a0f0) | plausibly `FakePhysics/Boost*` or `Score/Boost/*` — not certain which |

This doesn't rename anything new, but it's a reasonable prior for what fields those four
already-known functions are likely registering, one title later in the same series's tuning-variable
system — useful context if anyone writes up what those functions actually do.

## Verdict

No new Xbox addresses to add from this. Filed as reference material, same tier as the Burnout 2
cross-reference source paths but for tuning semantics rather than source-file/class identity.
