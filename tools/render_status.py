"""Render BUILD-STATUS.md and docs/status-chart.svg from the build machine's telemetry JSON.

usage: python3 tools/render_status.py telemetry.json REPO_DIR
"""
import json, sys, os, datetime

T = json.load(open(sys.argv[1])); repo = sys.argv[2]
TOTAL = 175187
LIBS = [('Development', 141928), ('Formalism', 18254), ('GroundTheory', 8507), ('ReciprocityTheory', 3845),
        ('CompanionTheory', 2027), ('PositivityTheory', 449), ('Lemmata', 167)]
PRICE = 1.56
START = datetime.datetime(2026, 11, 20, 23, 29)          # first proof file, UTC
now = datetime.datetime.utcnow()
HIST = sorted(T['history']); built = T['built']
t0 = HIST[0][0]
# rate over the last hour of history, in files per minute
recent = [p for p in HIST if p[0] >= HIST[-1][0] - 3600]
rate = (recent[-1][1] - recent[0][1]) / ((recent[-1][0] - recent[0][0]) / 60) if len(recent) > 1 and recent[-1][0] > recent[0][0] else 0
left_min = (TOTAL - built) / rate if rate > 0 else None
eta = now + datetime.timedelta(minutes=left_min) if left_min else None
LAUNCH = datetime.datetime(2026, 11, 20, 22, 40)          # instance launched, UTC
STOPPED_H = 0.77                                           # Spot interruption 02:06 to 02:12, not billed
cost = ((now - LAUNCH).total_seconds() / 3600 - STOPPED_H) * PRICE
BUILD_COST = ((datetime.datetime(2026, 11, 21, 20, 52) - LAUNCH).total_seconds() / 3600 - STOPPED_H) * PRICE
cost_end = cost + (left_min / 60 * PRICE if left_min else 0)
pct = 100 * built / TOTAL

def bar(frac, n=30):
    full = int(frac * n); part = frac * n - full
    blocks = ' ▏▎▍▌▋▊▉'
    return '█' * full + (blocks[int(part * 8)] if full < n else '') + '░' * (n - full - (1 if full < n else 0))

def fmt_d(m):
    h, mm = divmod(int(m), 60); return f'{h}h {mm:02d}m'

# ---------- the SVG chart ----------
W, H, L, R, TP, B = 900, 380, 70, 40, 64, 50
pw, ph = W - L - R, H - TP - B
hours_done = (HIST[-1][0] - t0) / 3600
hours_total = hours_done + (left_min / 60 if left_min else 0)
xmax = max(hours_total, hours_done, 1) * 1.04
X = lambda h: L + pw * h / xmax
Y = lambda n: TP + ph * (1 - n / TOTAL)
pts = ' '.join(f'{X((t - t0) / 3600):.1f},{Y(v):.1f}' for t, v in HIST)
area = f'{X(0):.1f},{Y(0):.1f} ' + pts + f' {X(hours_done):.1f},{Y(0):.1f}'
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="Inter, -apple-system, Segoe UI, sans-serif">',
       '<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8fa6ff" stop-opacity=".55"/><stop offset="1" stop-color="#8fa6ff" stop-opacity="0"/></linearGradient></defs>',
       f'<rect width="{W}" height="{H}" rx="16" fill="#0b0e17"/>',
       f'<text x="{L}" y="26" fill="#e8ecf5" font-size="16" font-weight="700">Proof files compiled</text>',
       f'<text x="{W - R}" y="26" fill="#9aa3b8" font-size="13" text-anchor="end">updated {now:%H:%M} UTC</text>']
for k in range(0, 6):
    n = TOTAL * k / 5; y = Y(n)
    svg.append(f'<line x1="{L}" x2="{W - R}" y1="{y:.1f}" y2="{y:.1f}" stroke="#ffffff" stroke-opacity=".07"/>')
    svg.append(f'<text x="{L - 8}" y="{y + 4:.1f}" fill="#7d869c" font-size="11" text-anchor="end">{int(n / 1000)}k</text>')
step = 2 if xmax > 10 else 1
h = 0
while h <= xmax:
    svg.append(f'<text x="{X(h):.1f}" y="{H - B + 18}" fill="#7d869c" font-size="11" text-anchor="middle">{h}h</text>'); h += step
if left_min:
    svg.append(f'<line x1="{X(hours_done):.1f}" y1="{Y(built):.1f}" x2="{X(hours_total):.1f}" y2="{Y(TOTAL):.1f}" stroke="#c79bff" stroke-width="2" stroke-dasharray="6 6"/>')
    svg.append(f'<circle cx="{X(hours_total):.1f}" cy="{Y(TOTAL):.1f}" r="5" fill="#c79bff"/>')
    svg.append(f'<text x="{X(hours_total) - 10:.1f}" y="{Y(TOTAL) + 20:.1f}" fill="#c79bff" font-size="12" text-anchor="end">projected finish {eta:%H:%M} UTC</text>')
svg.append(f'<polygon points="{area}" fill="url(#g)"/>')
svg.append(f'<polyline points="{pts}" fill="none" stroke="#8fa6ff" stroke-width="3" stroke-linejoin="round"/>')
svg.append(f'<circle cx="{X(hours_done):.1f}" cy="{Y(built):.1f}" r="6" fill="#8fe3b0"/>')
svg.append(f'<text x="{X(hours_done) + 10:.1f}" y="{Y(built) + 4:.1f}" fill="#8fe3b0" font-size="13" font-weight="700">{built:,}</text>')
svg.append(f'<line x1="{L}" x2="{W - R}" y1="{Y(TOTAL):.1f}" y2="{Y(TOTAL):.1f}" stroke="#8fe3b0" stroke-opacity=".35" stroke-dasharray="2 4"/>')
svg.append(f'<text x="{L + 6}" y="{Y(TOTAL) - 7:.1f}" fill="#8fe3b0" fill-opacity=".8" font-size="11">all 175,187 proof files</text>')
svg.append(f'<text x="{L + pw / 2:.0f}" y="{H - 10}" fill="#7d869c" font-size="11" text-anchor="middle">hours since the first proof file (23:29 UTC)</text>')
svg.append('</svg>')
# A new file name each update: GitHub caches images by path, so a redrawn file would not refresh.
cdir = os.path.join(repo, 'docs', 'status')
os.makedirs(cdir, exist_ok=True)
for old in os.listdir(cdir):
    if old.startswith('chart-') and old.endswith('.svg'): os.remove(os.path.join(cdir, old))
chart_name = f'chart-{now:%Y%m%d-%H%M}.svg'
open(os.path.join(cdir, chart_name), 'w').write('\n'.join(svg))
old_fixed = os.path.join(repo, 'docs', 'status-chart.svg')
if os.path.exists(old_fixed): os.remove(old_fixed)

# ---------- the page ----------
done = T['result'] != ''
ok = done and 'exit status 0' in T['result']
race = T.get('race', {}); race_tsv = race.get('tsv', ''); race_log = race.get('log', '')
race_rows = [r.split('\t') for r in race_tsv.strip().split('\n')[1:] if r.strip()] if race_tsv.strip() else []
# Status of each step of the plan: 'done', 'now', 'next' or 'stop'
st = {}
st['build'] = 'done' if ok else ('stop' if done else 'now')
st['export'] = 'done' if race_rows or 'export exit 0' in race_log else ('now' if ok else 'next')
st['race'] = 'done' if len(race_rows) >= 8 else ('now' if st['export'] == 'done' else 'next')
st['axioms'] = 'done' if 'axioms' in race_log.lower() and st['race'] == 'done' else ('now' if st['race'] == 'done' else 'next')
st['minify'] = 'next'
st['publish'] = 'next'
ICON = {'done': '✅ done', 'now': '🔵 **in progress**', 'next': '⏳ waiting', 'stop': '⚠️ stopped'}
NOW = {'export': '🔵 **Step 2 of 6: exporting the exact reduced form**', 'race': '🔵 **Step 3 of 6: Haskell vs Lean race running**', 'axioms': '🔵 **Step 4 of 6: listing axioms**'}
head = next((NOW[k] for k in ('export', 'race', 'axioms') if st[k] == 'now'), '✅ **Steps 1 to 4 done**') if ok else ('⚠️ **Build stopped**' if done else '🔵 **Step 1 of 6: compiling**')
STEPS = [
 ('build', '1', 'Build the original', f'Compile all 175,187 proof files, exactly as published. **{pct:.1f}%** so far.'),
 ('export', '2', 'Exact reduced form', 'Export the five main theorems with `lean4export`. The export holds exactly what the proof uses, measured by Lean itself.'),
 ('race', '3', 'Haskell vs Lean', "Check that export with **tenet-hs** (Haskell) and with Lean's own kernel, timed, peak memory recorded. Tenet (C#), tenet-jvm, Lean's paranoid mode, nanoda, con-leche and con-ron run in the same race."),
 ('axioms', '4', 'Axioms', 'List exactly which axioms the five theorems rest on.'),
 ('minify', '5', 'The smallest proof', 'Cut the source down to only the declarations in the export, rebuild that, and check it again with every kernel. The result is the smallest version of the proof that still compiles.'),
 ('publish', '6', 'Publish', 'Post the times, the verdicts and the exact sizes here.'),
]
MER = {'done': 'done', 'now': 'now', 'next': 'next', 'stop': 'stop'}
mer = ['```mermaid', 'flowchart LR']
labels = {'build': '1 Build the<br>original', 'export': '2 Exact<br>reduced form', 'race': '3 Haskell<br>vs Lean',
          'axioms': '4 Axioms', 'minify': '5 Smallest<br>proof', 'publish': '6 Publish'}
keys = [k for k, *_ in STEPS]
mer.append('  ' + ' --> '.join(f'{k}["{labels[k]}"]' for k in keys))
mer += ['  classDef done fill:#1f6f43,stroke:#8fe3b0,color:#fff',
        '  classDef now fill:#2b3f8f,stroke:#8fa6ff,color:#fff,stroke-width:3px',
        '  classDef next fill:#2a2f3d,stroke:#5b6378,color:#c9cfdc',
        '  classDef stop fill:#7a2a2a,stroke:#ff9b9b,color:#fff']
for k in keys: mer.append(f'  class {k} {MER[st[k]]}')
mer.append('```')

lines = [
 '# Live: checking the claimed Lean proof of the Riemann Hypothesis', '',
 '> **The goal:** find the exact, smallest form of the proof, then see whether **tenet-hs**, a Lean kernel '
 "written from scratch in Haskell, accepts it, and whether it is faster than Lean's own kernel.", '',
 (f'**Next up: the Haskell run** (step 3) starts by itself about **{eta:%H:%M} UTC**, as soon as the build finishes.' if eta and st['race'] == 'next' and not ok
  else ('**Next up: the Haskell run** (step 3) starts by itself as soon as the export is written.' if st['race'] == 'next' else ('**The race is on:** all 8 kernels are checking the 61.6 GB export at the same time, tenet-hs (Haskell) and Lean\'s own kernel among them.' if st['race'] == 'now' else ''))), '',
 f'{head} · updated every 10 minutes · last update **{now:%Y-%m-%d %H:%M} UTC**', '',
 '| The proof | Levent Alpöge, working with Claude ([remark.pdf](https://alpo.ge/remark.pdf)), announced 2026-11-20 |',
 '|---|---|',
 '| Source | byte-exact mirror [Deicyde/riemann-hypothesis](https://github.com/Deicyde/riemann-hypothesis) at `8b83d5e`, Lean 4.33.1, Mathlib v4.33.1 |',
 '| Size | 175,187 files, about 17.5 million lines, 1 docstring |',
 '| The five theorems checked | `riemannHypothesis`, `riemannZeta_eq_zero_re`, `LFunction_ne_zero_of_half_lt_re`, `LFunction_eq_zero_re`, `LFunction_eq_zero_re_of_isPrimitive` |',
 '| Build it yourself | [docs/BUILD-ORIGINAL.md](docs/BUILD-ORIGINAL.md): one script, about 21 hours and $35 on one AWS Spot machine |',
 '',
 '## The plan', '', *mer, '',
 '| | Step | What happens | Status | 💵 Cost |', '|:---:|---|---|---|---:|']
def wall_h(w):
    try:
        parts = [float(x) for x in w.split(':')]
    except ValueError:
        return 0.0
    sec = 0.0
    for x in parts: sec = sec * 60 + x
    return sec / 3600
T_BUILD_END = datetime.datetime(2026, 11, 21, 20, 52)
T_RACE_START = datetime.datetime(2026, 11, 21, 23, 22)
race_h = (now - T_RACE_START).total_seconds() / 3600
COST = {'build': BUILD_COST if ok else cost,
        'export': ((T_RACE_START if st['export'] == 'done' else now) - T_BUILD_END).total_seconds() / 3600 * PRICE if ok else None,
        'race': race_h * PRICE if st['race'] != 'next' else None}
def cost_cell(k):
    c = COST.get(k)
    if c is None: return 'not started' if k in COST else 'not started'
    return f'${c:.2f}' + (' so far' if st[k] == 'now' else '')
for k, n, name, what in STEPS:
    s_ = ICON[st[k]]
    if k in ('export', 'race') and st[k] == 'next' and eta:
        s_ = f'⏳ starts about **{eta:%H:%M} UTC**, when the build finishes'
    lines.append(f'| **{n}** | **{name}** | {what} | {s_} | {cost_cell(k)} |')
lines += ['', f'**Total so far: ${cost:.2f}**, at the Spot rate of about $1.56 an hour. The disk (now 600 GB) and its snapshots add about $2 a day.', '', 'Steps 2 to 4 are queued on the machine and start by themselves when the build succeeds. Step 5 follows from their output.', '']

import re as _re
if st['export'] == 'done':
    lines += ['## Step 2 result: the exact reduced form', '',
     'Exported from the unmodified build with `lean4export` 3.1.0 (Lean 4.33.1), in the no-network sandbox, '
     'starting from the five main theorems. This is everything the proof uses, measured by Lean itself, '
     "including the parts of Mathlib and Lean's core library it needs.", '',
     '| | |', '|---|---|',
     '| Declarations | **1,468,414**: 1,246,109 theorems, 214,238 definitions, 7,969 inductive types, 91 opaque, 4 quotient |',
     '| Axioms | **3, all Lean\'s standard ones:** `propext`, `Quot.sound`, `Classical.choice` |',
     '| Size | 61.6 GB of NDJSON, 1,065,214,329 expressions, 14,065,146 names |',
     '| Export time | 2 h 17 m, 163 GB peak memory, exit 0 |',
     '| sha256 | `4301ce4828d397c728e87f3e6a1251aa42abe5e12809bb9e0b73cc3d33072e7e` |', '']
KERNELS = [
 ('lean-kernel', "Lean's kernel", "Lean 4.36's own type checker, the reference"),
 ('lean-kernel-paranoid', 'Lean paranoid', 'the same kernel with extra checks'),
 ('nanoda', 'nanoda', 'independent kernel in Rust'),
 ('con-leche', 'con-leche', 'independent checker'),
 ('con-ron', 'con-ron', 'independent checker'),
 ('tenet', '**Tenet**', 'written from scratch in C# ([repo](https://github.com/keithadler/tenet))'),
 ('tenet-hs', '**tenet-hs**', 'written from scratch in **Haskell** ([repo](https://github.com/keithadler/tenet-hs))'),
 ('tenet-jvm', '**tenet-jvm**', 'written from scratch for the JVM ([repo](https://github.com/keithadler/tenet-jvm))'),
]
done_rows = {c[0]: c for c in race_rows if len(c) >= 6}
running = {c['name']: c for c in (T.get('checkers') or [])}
if st['export'] == 'done':
    lines += ['## Step 3: the kernel race, Haskell vs Lean', '',
     'Each checker reads the same 61.6 GB export and checks every declaration from scratch. Lean\'s kernel started '
     'alone at 23:22 UTC; at 00:38 the other seven were started alongside it, because each uses one core (Tenet uses '
     'many) and the machine has 192 vCPUs, so running them one at a time left it idle at the same hourly cost. Each '
     'runs in its own memory-capped sandbox. Running together can slow each a little (shared memory bandwidth); if '
     'two kernels finish close together, they will be re-timed alone.', '',
     '| # | Checker | What it is | Verdict | Wall time | CPU | Peak memory |', '|:---:|---|---|:---:|---:|---:|---:|']
    for n_, (key, name, what) in enumerate(KERNELS, 1):
        if key in done_rows:
            c = done_rows[key]
            verdict = '✅ accepts' if c[1] == '0' else f'❌ exit {c[1]}'
            lines.append(f'| {n_} | {name} | {what} | {verdict} | {c[2]} | {float(c[3]):,.0f} s | {c[5]} GB |')
        elif key in running:
            cur = running[key]
            cores = cur['cpu_s'] / cur['elapsed_s'] if cur['elapsed_s'] else 0
            lines.append(f"| {n_} | {name} | {what} | 🔵 **checking** | {fmt_d(cur['elapsed_s'] / 60)} so far | {cur['cpu_s']:,} s (~{cores:.0f} cores) | {cur['rss_gb']:.0f} GB now |")
        else:
            lines.append(f'| {n_} | {name} | {what} | ⏳ queued | | | |')
    lines.append('')

lines += [
] + ([
 '## Step 1: the build ✅ done', '',
 f'`{bar(1, 40)}`  **175,187** of 175,187 proof files · `Build completed successfully (183893 jobs)`', '',
 '| ⏱ Compiling time | 🏁 Finished (UTC) | 💵 Build cost | 💵 Spent so far | ❌ Errors | 🚫 sorry |',
 '|:---:|:---:|:---:|:---:|:---:|:---:|',
 f"| about 21 h | 2026-11-21 20:52 | ${BUILD_COST:.2f} | ${cost:.2f} | {T['errors']} | 0 |", '',
 'Spent so far keeps counting while the machine runs steps 2 to 4.', ''] if ok else [
 f'## Step 1: the build, {pct:.1f}%', '',
 f'`{bar(built / TOTAL, 40)}`  **{built:,}** of 175,187 proof files', '',
 '| ⏱ Time left | 🏁 Finish (UTC) | ⚡ Rate | 💵 Spent | 💵 Projected total | ❌ Errors |',
 '|:---:|:---:|:---:|:---:|:---:|:---:|',
 f"| {fmt_d(left_min) if left_min else '?'} | {eta.strftime('%H:%M') if eta else '?'} | {rate:.0f} files/min | ${cost:.2f} | ${cost_end:.0f} | {T['errors']} |", '']) + [
 f'![Proof files compiled over time](docs/status/{chart_name})', '',
 '<details><summary><b>By library</b></summary>', '',
 '| Library | Built | Progress |', '|---|---:|---|']
for name, tot in LIBS:
    b = T['lib'].get(name, 0)
    lines.append(f'| `{name}` | {b:,} / {tot:,} | `{bar(min(b / tot, 1), 20)}` {100 * b / tot:.0f}% |')
lines += ['', '</details>', '',
 '<details><summary><b>The machine</b></summary>', '',
 '| | |', '|---|---|',
 '| Instance | AWS `m6a.48xlarge` Spot, Ohio, about $1.56/hour |',
 f"| CPUs | 192 vCPUs (96 cores), load {T['load']:.0f}, {T['lean_procs']} Lean processes running |",
 f"| Memory | {T['mem_used_gb']:.0f} GB used of {T['mem_total_gb']:.0f} GB |",
 f"| Disk | {T['disk_free_gb']:.0f} GB free of {T['disk_total_gb']:.0f} GB |",
 '| Sandbox | bubblewrap: no network, everything read-only except the build folder |',
 '| Safety net | the disk survives termination, and is snapshotted every 2 hours |', '',
 '</details>', '',
 ]
if not ok:
    lines += ['<details><summary><b>Just compiled</b></summary>', ''] + [f'- `{m}`' for m in reversed(T['recent'])] + ['', '</details>', '']
lines += [
 '<details><summary><b>Log: what went wrong and how it was handled</b></summary>', '',
 "- **2026-11-20 23:29 UTC:** started compiling the original proof, after the source-level reduction turned out to drop real dependencies ([why](README.md)).",
 "- **00:39 to 00:49:** disk full. Lake's per-module `.setup.json` files reached 92 GB (about 4.6 MB each, listing every import). They are now deleted as modules finish; nothing built was lost.",
 "- **01:45:** status counter fixed. Lake re-prints warnings for modules already built, which the old counter counted twice.",
 "- **02:06 to 02:12:** AWS reclaimed the Spot machine. It stopped with its disk kept, and came back on its own when capacity returned; the build resumed with nothing lost. Everything now restarts by itself after any interruption, and progress is counted from compiled files on disk.",
 "- **2026-11-21 09:21 to 09:24:** a second Spot interruption. The machine resumed the build by itself within a minute of coming back.",
 "- **10:25 to 10:34:** a third Spot interruption, with no capacity for 9 minutes. Resumed by itself again; nothing lost.",
 "- **13:04 to 13:32:** a fourth Spot interruption, 28 minutes this time. Resumed by itself again; nothing lost.",
 "- **20:52:38: build finished.** `Build completed successfully (183893 jobs)`: all 175,187 proof files, 0 errors, no `sorry`, 6 h 56 m of compiling since the last restart. The export (step 2) started at 20:53.",
 "- **21:30:** the export file was growing toward the disk's limit (51 GB free, about 0.66 GB a minute). The disk was grown from 200 GB to 600 GB while running; nothing stopped.",
 "- **23:10: export finished.** 1,468,414 declarations, 61.6 GB, exit 0, in 2 h 17 m. Only Lean's three standard axioms appear.",
 "- **23:22: the kernel race started** with Lean's kernel.",
 "- **00:38:** switched to a parallel race. Each checker uses one core, so the other seven now run alongside Lean's kernel instead of after it, each in its own memory-capped sandbox. Same hourly cost, results hours sooner.", '',
 '</details>', '',
 'Rate and finish come from the last hour of the timestamped build log. Build it yourself: [docs/BUILD-ORIGINAL.md](docs/BUILD-ORIGINAL.md).']
open(os.path.join(repo, 'BUILD-STATUS.md'), 'w').write('\n'.join(lines) + '\n')
print(f'{built} built, {pct:.1f}%, rate {rate:.0f}/min, finish {eta:%H:%M} UTC' if eta else f'{built} built')
