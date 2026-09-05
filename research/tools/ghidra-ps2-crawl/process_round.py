import re, sys, pickle

round_file = sys.argv[1]
lookup = pickle.load(open('lookup.pkl', 'rb'))
state = pickle.load(open('state.pkl', 'rb'))
visited = state['visited']
found = state['found']

OFFSETS = [0xc0, 0xd0, 0xb0, 0xe0, 0xa0, 0xf0, 0x90, 0x100, 0x0]

text = open(round_file, encoding='latin1').read()
blocks = re.split(r'===FUNC:(\w+)===\n', text)[1:]
new_names = []
next_frontier = set()

for i in range(0, len(blocks), 2):
    src_addr = blocks[i]
    body = blocks[i+1]
    callees = set(re.findall(r'FUN_([0-9a-fA-F]{8})', body))
    for c in callees:
        c = c.lower()
        if c in visited:
            continue
        c_int = int(c, 16)
        for off in OFFSETS:
            mapped = format(c_int + off, '08x')
            if mapped in lookup:
                cls, sig = lookup[mapped]
                found[c] = (cls, sig, '', off)
                new_names.append((c, cls, sig, off, src_addr))
                next_frontier.add(c)
                break
        visited.add(c)

pickle.dump({'visited': visited, 'found': found}, open('state.pkl', 'wb'))

print(f"round processed: {len(blocks)//2} functions, {len(new_names)} new names found, {len(next_frontier)} to expand")
for c, cls, sig, off, src in new_names:
    print(f"  {c} (+0x{off:x}) -> {cls}::{sig}   [found via caller {src}]")

with open('next_frontier.txt', 'w') as f:
    for a in sorted(next_frontier):
        f.write(a + "\n")
