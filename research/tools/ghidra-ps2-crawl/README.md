# PS2 call-graph crawl tooling

Ghidra headless scripts used to build [research/data/ps2-confirmed-callgraph.csv](../../data/ps2-confirmed-callgraph.csv).
See [research/notes/ps2-xbox-binding.md](../../notes/ps2-xbox-binding.md) for methodology and results.

Requires a Ghidra project with the PS2 executable (`DNAT_200.45` — the file `SYSTEM.CNF`'s `BOOT2`
line points to) imported with the `r5900:LE:32:default` processor from
[ghidra-emotionengine-reloaded](https://github.com/chaoticgd/ghidra-emotionengine-reloaded)
(stock Ghidra's generic MIPS module misparses the Emotion Engine's MMI/VU0 instructions).

- `BatchDecompile.java` — takes a text file of one address per line, force-disassembles+decompiles
  each (creating a function there if none exists yet), writes `===FUNC:<addr>===` / `REALADDR:<addr>`
  / decompiled C blocks to an output file. One JVM invocation for many addresses, instead of one per
  address.
- `DecompileAt2.java` — single-address version of the above, for side-by-side PS2/Xbox comparisons.
- `DumpFuncs.java` — dumps every function Ghidra's own analysis has found (address, name, size) —
  used to validate candidate addresses against real function starts rather than trusting forced
  `createFunction` calls blindly.
- `FindScalar.java` — searches every function for literal instruction-operand scalars matching a
  given set of hex values. Didn't pan out for cross-architecture constant matching in practice (see
  the binding note's "didn't work" section) but may still be useful for other searches.
- `process_round.py` — drives the call-graph crawl: given a `BatchDecompile.java` output file, a
  pickled `lookup.pkl` (address → `Class::method` built from `DNAT_200.MAP`), and a pickled
  `state.pkl` (visited/found sets), extracts callees from each decompiled body, tries the known
  offset corrections against the lookup table, records new hits, and writes the next frontier file.
  Run in a loop, each round feeding a fresh `BatchDecompile.java` pass, until the frontier is empty.

Usage sketch (from a project directory containing `lookup.pkl`, built once from `DNAT_200.MAP`):

```bash
# seed state.pkl with your starting anchors (real Ghidra addresses, not map addresses), then:
analyzeHeadless <ghidra_project_dir> <project_name> -process <program> -noanalysis \
    -scriptPath <this_dir> -postScript BatchDecompile.java frontier.txt round.txt
python3 process_round.py round.txt   # prints new finds, writes next_frontier.txt
# repeat with next_frontier.txt as the new frontier.txt, until it's empty
```
