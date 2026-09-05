import html

csv_path = "/home/shipa/Projects/sp00nznet-burnout3/src/docs/decomp-atlas/functions.csv"
out_path = "/home/shipa/Projects/sp00nznet-burnout3/src/docs/decomp-atlas/function-atlas.html"

csv_text = open(csv_path, "r", encoding="utf-8").read()
assert "</script" not in csv_text.lower()

# Manual status overrides, reflecting actual project state (see repo notes/).
# address -> status ("done" | "in_progress")
# "done" = fully understood and confirmed (either reimplemented & hooked in reburn3, or -- for
# game-logic functions that don't need reimplementing -- conclusively diagnosed).
DONE = {
    "0003c8a0",  # CB3GraphicsManager::ConstructLTCG -- reimplemented & hooked in reburn3
    "000110e0",  # async read-status gate -- confirmed correct; was a real file-open failure, not a bug
    "000214b0",  # its error-screen handler -- confirmed correct
}
IN_PROGRESS = set()

TEMPLATE = r"""<title>Burnout 3 Function Atlas</title>
<style>
  :root {
    --bg: #eef1ef;
    --surface: #ffffff;
    --surface-2: #f5f7f5;
    --border: #d7dcd8;
    --text: #12181a;
    --text-muted: #55625f;
    --text-faint: #8a9490;
    --st-unknown: #c9cfcb;
    --st-identified: #2f6fed;
    --st-known: #8b5cf6;
    --st-progress: #d9822b;
    --st-done: #1f9d55;
    --focus: #2f6fed;
    --mono: "IBM Plex Mono", ui-monospace, "Cascadia Mono", Consolas, monospace;
    --sans: "IBM Plex Sans", -apple-system, "Segoe UI", sans-serif;
  }

  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
      --bg: #0b0f0e;
      --surface: #121917;
      --surface-2: #0e1413;
      --border: #223330;
      --text: #e7f3ee;
      --text-muted: #93a6a0;
      --text-faint: #5c6c67;
      --st-unknown: #2b3330;
      --st-identified: #5b9dff;
      --st-known: #a78bfa;
      --st-progress: #f2a93b;
      --st-done: #35d9a4;
      --focus: #5b9dff;
    }
  }

  :root[data-theme="dark"] {
    --bg: #0b0f0e;
    --surface: #121917;
    --surface-2: #0e1413;
    --border: #223330;
    --text: #e7f3ee;
    --text-muted: #93a6a0;
    --text-faint: #5c6c67;
    --st-unknown: #2b3330;
    --st-identified: #5b9dff;
    --st-known: #a78bfa;
    --st-progress: #f2a93b;
    --st-done: #35d9a4;
    --focus: #5b9dff;
  }

  * { box-sizing: border-box; }

  body {
    margin: 0;
    background: var(--bg);
    color: var(--text);
    font-family: var(--sans);
    -webkit-font-smoothing: antialiased;
  }

  .wrap {
    max-width: 1180px;
    margin: 0 auto;
    padding: 2.5rem 1.5rem 4rem;
    display: flex;
    flex-direction: column;
    gap: 1.75rem;
  }

  header.page {
    display: flex;
    flex-direction: column;
    gap: 0.6rem;
  }

  .eyebrow {
    font-family: var(--mono);
    font-size: 0.72rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--text-faint);
  }

  h1 {
    font-family: var(--mono);
    font-weight: 600;
    font-size: clamp(1.6rem, 3vw, 2.2rem);
    margin: 0;
    letter-spacing: -0.01em;
    text-wrap: balance;
  }

  .dek {
    color: var(--text-muted);
    font-size: 0.98rem;
    line-height: 1.55;
    max-width: 64ch;
  }

  .dek a { color: var(--st-identified); text-decoration-color: color-mix(in srgb, var(--st-identified) 40%, transparent); }
  .dek a:hover { text-decoration-color: var(--st-identified); }

  .stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1px;
    background: var(--border);
    border: 1px solid var(--border);
    border-radius: 10px;
    overflow: hidden;
  }

  .stat {
    background: var(--surface);
    padding: 0.9rem 1.1rem;
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .stat .n {
    font-family: var(--mono);
    font-variant-numeric: tabular-nums;
    font-size: 1.5rem;
    font-weight: 600;
    letter-spacing: -0.01em;
  }

  .stat .n.identified { color: var(--st-identified); }
  .stat .n.known { color: var(--st-known); }
  .stat .n.progress { color: var(--st-progress); }
  .stat .n.done { color: var(--st-done); }

  .stat .l {
    font-size: 0.74rem;
    color: var(--text-muted);
    letter-spacing: 0.01em;
  }

  .panel {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.1rem;
    display: flex;
    flex-direction: column;
    gap: 0.9rem;
  }

  .panel-head {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem;
  }

  .legend {
    display: flex;
    flex-wrap: wrap;
    gap: 1.1rem;
    font-size: 0.82rem;
    color: var(--text-muted);
  }

  .legend .item { display: flex; align-items: center; gap: 0.45rem; }
  .swatch { width: 0.68rem; height: 0.68rem; border-radius: 2px; flex: none; }
  .swatch.unknown { background: var(--st-unknown); }
  .swatch.identified { background: var(--st-identified); }
  .swatch.known { background: var(--st-known); }
  .swatch.progress { background: var(--st-progress); }
  .swatch.done { background: var(--st-done); }

  .search {
    position: relative;
    width: min(260px, 100%);
  }

  .search input {
    width: 100%;
    background: var(--surface-2);
    border: 1px solid var(--border);
    color: var(--text);
    font-family: var(--mono);
    font-size: 0.85rem;
    padding: 0.5rem 0.7rem;
    border-radius: 7px;
    outline: none;
  }

  .search input::placeholder { color: var(--text-faint); }

  .search input:focus {
    border-color: var(--focus);
    box-shadow: 0 0 0 3px color-mix(in srgb, var(--focus) 20%, transparent);
  }

  .search .count {
    position: absolute;
    right: 0.6rem;
    top: 50%;
    transform: translateY(-50%);
    font-family: var(--mono);
    font-size: 0.72rem;
    color: var(--text-faint);
    pointer-events: none;
  }

  .canvas-wrap {
    position: relative;
    width: 100%;
    aspect-ratio: 16 / 8.4;
    border-radius: 7px;
    overflow: hidden;
    background: var(--surface-2);
    cursor: crosshair;
  }

  canvas { display: block; width: 100%; height: 100%; }

  .tip {
    position: fixed;
    pointer-events: none;
    background: var(--text);
    color: var(--bg);
    font-family: var(--mono);
    font-size: 0.76rem;
    line-height: 1.5;
    padding: 0.5rem 0.65rem;
    border-radius: 6px;
    max-width: 280px;
    opacity: 0;
    transform: translate(-50%, -100%);
    transition: opacity 0.08s ease;
    z-index: 10;
    white-space: pre;
  }

  .tip.show { opacity: 1; }

  .foot {
    color: var(--text-faint);
    font-size: 0.8rem;
    line-height: 1.6;
  }

  .foot a { color: var(--text-muted); }
  .foot a:hover { color: var(--st-identified); }

  @media (prefers-reduced-motion: reduce) {
    .tip { transition: none; }
  }
</style>

<div class="wrap">
  <header class="page">
    <div class="eyebrow">sp00nznet/burnout3 fork &middot; static analysis</div>
    <h1>Burnout 3 Function Atlas</h1>
    <p class="dek">
      Every function Ghidra found in <code>default.xbe</code>, one rectangle each, sized by byte length.
      Grey is untouched. Blue is stock Microsoft XDK library code Cxbx-Reloaded's own database already
      recognizes &mdash; not worth reverse-engineering. Purple is Burnout 3's own game code with a real
      name recovered by the <a href="https://github.com/mxmstr/Burnout3Recomp" target="_blank" rel="noopener">Burnout3Recomp</a>
      project. Orange is under active investigation right now. Green is reimplemented and confirmed
      working. See
      <a href="https://github.com/shipa-2/burnout3" target="_blank" rel="noopener">the repository</a>
      for methodology.
    </p>
  </header>

  <div class="stats">
    <div class="stat">
      <div class="n">__TOTAL__</div>
      <div class="l">functions found</div>
    </div>
    <div class="stat">
      <div class="n identified">__IDENTIFIED__</div>
      <div class="l">library code (__IDENTIFIED_PCT__%)</div>
    </div>
    <div class="stat">
      <div class="n known">__KNOWN__</div>
      <div class="l">game code, name recovered</div>
    </div>
    <div class="stat">
      <div class="n progress">__PROGRESS__</div>
      <div class="l">in progress right now</div>
    </div>
    <div class="stat">
      <div class="n done">__DONE__</div>
      <div class="l">reimplemented &amp; confirmed</div>
    </div>
    <div class="stat">
      <div class="n">__UNKNOWN__</div>
      <div class="l">still untouched</div>
    </div>
  </div>

  <div class="panel">
    <div class="panel-head">
      <div class="legend">
        <span class="item"><span class="swatch unknown"></span>Unknown</span>
        <span class="item"><span class="swatch identified"></span>Library code</span>
        <span class="item"><span class="swatch known"></span>Game code, named</span>
        <span class="item"><span class="swatch progress"></span>In progress</span>
        <span class="item"><span class="swatch done"></span>Done</span>
      </div>
      <div class="search">
        <input id="search" type="text" placeholder="Filter by name or address&hellip;" autocomplete="off" spellcheck="false" />
        <span class="count" id="search-count"></span>
      </div>
    </div>
    <div class="canvas-wrap">
      <canvas id="tree"></canvas>
    </div>
  </div>

  <p class="foot">
    Layout: squarified treemap, area &prop; function byte size. Base data from a Ghidra headless
    auto-analysis export (<code>docs/functions.csv</code>). Library-code identification via
    Cxbx-Reloaded's <a href="https://github.com/Cxbx-Reloaded/XbSymbolDatabase" target="_blank" rel="noopener">XbSymbolDatabase</a>;
    game-code names via <a href="https://github.com/mxmstr/Burnout3Recomp" target="_blank" rel="noopener">Burnout3Recomp</a>
    (built on <a href="https://github.com/mxmstr/XenonRecomp" target="_blank" rel="noopener">mxmstr's x86 fork of XenonRecomp</a>).
    Progress/done status is hand-tracked against this project's own notes, not automated. Hover a
    cell for its address, name and size; filter narrows the map without reshuffling it, so a search
    stays legible against the whole binary's shape.
  </p>
</div>

<div class="tip" id="tip"></div>

<script type="text/plain" id="csv-data">__CSV__</script>
<script>
(function () {
  "use strict";

  var raw = document.getElementById("csv-data").textContent.trim();
  var lines = raw.split("\n");
  lines.shift(); // header

  var DONE = new Set(__DONE_JSON__);
  var IN_PROGRESS = new Set(__PROGRESS_JSON__);

  var data = lines.map(function (line) {
    // address,name,size,named,source -- name never contains a comma (Ghidra/community identifiers only)
    var parts = line.split(",");
    var address = parts[0];
    var name = parts[1];
    var size = parseInt(parts[2], 10);
    var namedFlag = parts[3] === "true";
    var source = parts[4] || "";

    var status = "unknown";
    if (DONE.has(address)) status = "done";
    else if (IN_PROGRESS.has(address)) status = "progress";
    else if (source === "community") status = "known";
    else if (namedFlag) status = "identified";

    return {
      address: address,
      name: name,
      size: isNaN(size) || size <= 0 ? 1 : size,
      status: status
    };
  });

  // ---- squarified treemap ----
  function squarify(items, x, y, w, h) {
    var rects = [];
    var total = items.reduce(function (s, d) { return s + d.size; }, 0);
    if (total <= 0 || items.length === 0) return rects;

    var sorted = items.slice().sort(function (a, b) { return b.size - a.size; });
    var scale = (w * h) / total;

    function worst(row, rowSize, lengthSide) {
      var max = -Infinity, min = Infinity;
      row.forEach(function (d) {
        var area = d.size * scale;
        var side = area / lengthSide;
        if (side > max) max = side;
        if (side < min) min = side;
      });
      var s2 = rowSize * rowSize;
      var l2 = lengthSide * lengthSide;
      return Math.max((l2 * max) / s2, s2 / (l2 * min));
    }

    var cx = x, cy = y, cw = w, ch = h;
    var i = 0;
    while (i < sorted.length) {
      var lengthSide = Math.min(cw, ch);
      var row = [sorted[i]];
      var rowSize = sorted[i].size;
      var bestWorst = worst(row, rowSize, lengthSide);
      var j = i + 1;
      while (j < sorted.length) {
        var testRow = row.concat([sorted[j]]);
        var testSize = rowSize + sorted[j].size;
        var w2 = worst(testRow, testSize, lengthSide);
        if (w2 <= bestWorst) {
          row = testRow; rowSize = testSize; bestWorst = w2; j++;
        } else break;
      }

      var rowArea = rowSize * scale;
      if (cw >= ch) {
        var rowW = rowArea / ch;
        var ry = cy;
        row.forEach(function (d) {
          var rh = (d.size * scale) / rowW;
          rects.push({ d: d, x: cx, y: ry, w: rowW, h: rh });
          ry += rh;
        });
        cx += rowW; cw -= rowW;
      } else {
        var rowH = rowArea / cw;
        var rx = cx;
        row.forEach(function (d) {
          var rw = (d.size * scale) / rowH;
          rects.push({ d: d, x: rx, y: cy, w: rw, h: rowH });
          rx += rw;
        });
        cy += rowH; ch -= rowH;
      }
      i = j;
    }
    return rects;
  }

  var canvas = document.getElementById("tree");
  var wrap = canvas.parentElement;
  var ctx = canvas.getContext("2d");
  var tip = document.getElementById("tip");
  var searchInput = document.getElementById("search");
  var searchCount = document.getElementById("search-count");

  var rects = [];
  var dpr = Math.max(1, window.devicePixelRatio || 1);
  var W = 0, H = 0;

  function colors() {
    var cs = getComputedStyle(document.documentElement);
    return {
      unknown: cs.getPropertyValue("--st-unknown").trim(),
      identified: cs.getPropertyValue("--st-identified").trim(),
      known: cs.getPropertyValue("--st-known").trim(),
      progress: cs.getPropertyValue("--st-progress").trim(),
      done: cs.getPropertyValue("--st-done").trim()
    };
  }

  function layout() {
    var r = wrap.getBoundingClientRect();
    W = Math.max(1, Math.round(r.width));
    H = Math.max(1, Math.round(r.height));
    canvas.width = W * dpr;
    canvas.height = H * dpr;
    rects = squarify(data, 0, 0, W, H);
    draw();
  }

  var query = "";

  function draw() {
    var c = colors();
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, W, H);

    rects.forEach(function (r) {
      var d = r.d;
      var matches = query === "" ||
        d.name.toLowerCase().indexOf(query) !== -1 ||
        d.address.toLowerCase().indexOf(query) !== -1;

      ctx.globalAlpha = matches ? 1 : 0.14;
      ctx.fillStyle = c[d.status];
      var pad = r.w > 3 && r.h > 3 ? 0.5 : 0;
      ctx.fillRect(r.x + pad, r.y + pad, Math.max(0, r.w - pad * 2), Math.max(0, r.h - pad * 2));
    });
    ctx.globalAlpha = 1;
  }

  function findAt(px, py) {
    for (var i = 0; i < rects.length; i++) {
      var r = rects[i];
      if (px >= r.x && px <= r.x + r.w && py >= r.y && py <= r.y + r.h) return r;
    }
    return null;
  }

  var STATUS_LABEL = {
    unknown: "unknown",
    identified: "identified (XbSymbolDatabase)",
    known: "name recovered (Burnout3Recomp)",
    progress: "in progress",
    done: "done"
  };

  canvas.addEventListener("mousemove", function (ev) {
    var b = canvas.getBoundingClientRect();
    var px = ev.clientX - b.left, py = ev.clientY - b.top;
    var hit = findAt(px, py);
    if (!hit) { tip.classList.remove("show"); return; }
    var d = hit.d;
    tip.textContent =
      d.name + "\n" +
      "0x" + d.address + "  ·  " + d.size + " bytes\n" +
      STATUS_LABEL[d.status];
    tip.style.left = ev.clientX + "px";
    tip.style.top = (ev.clientY - 12) + "px";
    tip.classList.add("show");
  });

  canvas.addEventListener("mouseleave", function () {
    tip.classList.remove("show");
  });

  searchInput.addEventListener("input", function () {
    query = searchInput.value.trim().toLowerCase();
    if (query === "") {
      searchCount.textContent = "";
    } else {
      var n = data.filter(function (d) {
        return d.name.toLowerCase().indexOf(query) !== -1 || d.address.toLowerCase().indexOf(query) !== -1;
      }).length;
      searchCount.textContent = n;
    }
    draw();
  });

  window.addEventListener("resize", layout);
  layout();

  if (window.matchMedia) {
    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", draw);
  }
})();
</script>
"""

lines_all = open(csv_path, encoding="utf-8").read().strip().split("\n")
data_lines = lines_all[1:]
total = len(data_lines)

def addr_of(line):
    return line.split(",")[0]

identified = 0
known = 0
for l in data_lines:
    parts = l.split(",")
    addr = parts[0]
    named_flag = parts[3] == "true"
    source = parts[4] if len(parts) > 4 else ""
    if addr in DONE or addr in IN_PROGRESS:
        continue
    if source == "community":
        known += 1
    elif named_flag:
        identified += 1

done_n = len(DONE)
progress_n = len(IN_PROGRESS)
unknown_n = total - identified - known - done_n - progress_n
identified_pct = round(100 * identified / total, 1)

import json
out = (TEMPLATE
    .replace("__CSV__", csv_text)
    .replace("__TOTAL__", f"{total:,}")
    .replace("__IDENTIFIED__", f"{identified:,}")
    .replace("__IDENTIFIED_PCT__", str(identified_pct))
    .replace("__KNOWN__", f"{known:,}")
    .replace("__PROGRESS__", str(progress_n))
    .replace("__DONE__", str(done_n))
    .replace("__UNKNOWN__", f"{unknown_n:,}")
    .replace("__DONE_JSON__", json.dumps(sorted(DONE)))
    .replace("__PROGRESS_JSON__", json.dumps(sorted(IN_PROGRESS)))
)

open(out_path, "w", encoding="utf-8").write(out)
print("wrote", out_path, len(out), "bytes")
print("total", total, "identified", identified, "known", known, "progress", progress_n, "done", done_n, "unknown", unknown_n)
