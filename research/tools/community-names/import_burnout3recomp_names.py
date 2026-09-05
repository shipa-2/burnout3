#!/usr/bin/env python3
"""
Merge function names from mxmstr/Burnout3Recomp's x86_func_mapping.cpp into docs/functions.csv.

Only fills in names for functions this repo doesn't already have a name for (i.e. still
`FUN_xxxxxxxx`, `named=false`) -- addresses already identified as Microsoft XDK library code
(via XbSymbolDatabase) keep their existing name/source untouched, even if Burnout3Recomp also
names them (it correctly recognizes plenty of library functions too, which isn't the interesting
part of that project's work for our purposes).

Usage:
    curl -o /tmp/x86_func_mapping.cpp \\
        https://raw.githubusercontent.com/mxmstr/Burnout3Recomp/main/Burnout3RecompLib/x86_func_mapping.cpp
    python3 import_burnout3recomp_names.py /tmp/x86_func_mapping.cpp docs/functions.csv
"""
import csv
import re
import sys

MAPPING_ENTRY = re.compile(r"\{\s*0x([0-9A-Fa-f]+),\s*(\w+)\s*\}")


def load_community_names(mapping_cpp_path):
    names = {}
    with open(mapping_cpp_path, encoding="utf-8", errors="replace") as f:
        for line in f:
            m = MAPPING_ENTRY.search(line)
            if not m:
                continue
            name = m.group(2)
            if name.startswith("sub_"):
                continue  # unnamed placeholder, nothing to import
            addr = m.group(1).lower().zfill(8)
            names[addr] = name
    return names


def merge(functions_csv_path, community_names):
    with open(functions_csv_path, newline="") as f:
        rows = list(csv.DictReader(f))

    newly_named = 0
    for row in rows:
        if row.get("named") == "true":
            row.setdefault("source", "")
            if not row["source"]:
                row["source"] = "xbsymboldb"
            continue  # keep library-identified rows untouched
        addr = row["address"]
        if addr in community_names:
            row["name"] = community_names[addr]
            row["source"] = "community"
            newly_named += 1
        else:
            row.setdefault("source", "")

    with open(functions_csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["address", "name", "size", "named", "source"])
        w.writeheader()
        w.writerows(rows)

    return newly_named, len(rows)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    mapping_cpp, functions_csv = sys.argv[1], sys.argv[2]
    community_names = load_community_names(mapping_cpp)
    newly_named, total = merge(functions_csv, community_names)
    print(f"community mapping entries with real names: {len(community_names)}")
    print(f"newly named in {functions_csv}: {newly_named} of {total} total rows")
