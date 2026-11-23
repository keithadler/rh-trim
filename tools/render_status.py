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
st['minify'] = 'now'
st['publish'] = 'next'
ICON = {'done': '✅ done', 'now': '🔵 **in progress**', 'next': '⏳ waiting', 'stop': '⚠️ stopped'}
NOW = {'export': '🔵 **Step 2 of 6: exporting the exact reduced form**', 'race': '🔵 **Step 3 of 6: Haskell vs Lean race running**', 'axioms': '🔵 **Step 4 of 6: listing axioms**'}
head = next((NOW[k] for k in ('export', 'race', 'axioms') if st[k] == 'now'), '✅ **Steps 1 to 4 done**') if ok else ('⚠️ **Build stopped**' if done else '🔵 **Step 1 of 6: compiling**')
STEPS = [
 ('build', '1', 'Build the original', f'Compile all 175,187 proof files, exactly as published. **{pct:.1f}%** so far.'),
 ('export', '2', 'Exact reduced form', 'Export the five main theorems with `lean4export`. The export holds exactly what the proof uses, measured by Lean itself.'),
 ('race', '3', 'Haskell vs Lean', "Check that export with **tenet-hs** (Haskell) and with Lean's own kernel, timed, peak memory recorded. Tenet (C#), tenet-jvm, Lean's paranoid mode, nanoda, con-leche and con-ron run in the same race."),
 ('axioms', '4', 'Axioms', 'List exactly which axioms the five theorems rest on.'),
 ('minify', '5', 'The smallest proof', 'Cut the source to only what the export says the theorems use, merge repeated theorems, rebuild, and check it with Tenet, then the other kernels. **Building in automatic repair rounds; live numbers in the counter at the top of the README.** [Details](docs/MINIFY.md)'),
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
  else ('**Next up: the Haskell run** (step 3) starts by itself as soon as the export is written.' if st['race'] == 'next' else ('**✅ Tenet (C#, written from scratch) accepts the whole proof:** 1,468,414 declarations, 0 failed, 1 h 0 m. Still checking: Lean\'s kernel, paranoid mode, nanoda and **tenet-hs (Haskell)**.' if st['race'] == 'now' else ''))), '',
 f'{head} · updated every 2 minutes · last update **{now:%Y-%m-%d %H:%M} UTC**', '',
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
 ('con-leche', 'con-leche', 'independent checker, formally verified mode'),
 ('con-ron', 'con-ron', 'independent checker, formally verified mode'),
 ('con-leche-trusted', 'con-leche, trusted mode', 'every check the official kernel does, outside its formal theorem'),
 ('con-ron-trusted', 'con-ron, trusted mode', 'the same, for con-ron'),
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
            declined = 'declined' in (race.get('log', '') + '') and key.startswith(('con-leche', 'con-ron')) and c[1] == '2'
            verdict = '✅ accepts' if c[1] == '0' else ('⚪ declined: no support for reflexive inductive types' if declined else f'❌ exit {c[1]}')
            if key == 'tenet-jvm' and c[1] == '143':
                verdict = '⏸ stopped: stuck about 90 min reading one declaration while memory grew; not a verdict'
            if c[1] == '143' and not c[2]:
                lines.append(f'| {n_} | {name} | {what} | ⏹ stopped at 05:37 UTC by an AWS Spot interruption after about 5 h; no verdict | | | |')
                continue
            cpu = f'{float(c[3]):,.0f} s' if c[3] else ''
            lines.append(f'| {n_} | {name} | {what} | {verdict} | {c[2]} | {cpu} | {c[5]} GB |')
        elif key in running:
            cur = running[key]
            cores = cur['cpu_s'] / cur['elapsed_s'] if cur['elapsed_s'] else 0
            lines.append(f"| {n_} | {name} | {what} | 🔵 **checking** | {fmt_d(cur['elapsed_s'] / 60)} so far | {cur['cpu_s']:,} s (~{cores:.0f} cores) | {cur['rss_gb']:.0f} GB now |")
        else:
            lines.append(f'| {n_} | {name} | {what} | ⏳ queued | | | |')
    lines.append('')

# ---------- the second machine's race (rh-kernels), read from /tmp/rh-tele2.txt
try:
    t2 = open('/tmp/rh-tele2.txt', encoding='utf-8').read()
except OSError:
    t2 = ''
if t2.strip():
    parts2 = t2.split('===')
    tsv, ps = parts2[0], (parts2[1] if len(parts2) > 1 else '')
    posmap = {}
    for line in (parts2[2] if len(parts2) > 2 else '').strip().split('\n'):
        f = line.split()
        if len(f) == 3 and f[1].isdigit(): posmap[f[0]] = max(posmap.get(f[0], 0), int(f[1]) / int(f[2]))
    jvm_count = int((parts2[3] if len(parts2) > 3 else '0').strip() or 0)
    done2 = [r.split('\t') for r in tsv.strip().split('\n')[1:] if r.strip()]
    run2 = []
    for line in ps.strip().split('\n'):
        f = line.split(None, 2)
        if len(f) == 3:
            nm = 'Lean paranoid' if 'paranoid' in f[2] else ("Lean's kernel" if 'leanchecker' in f[2] else ('tenet-hs (Haskell)' if 'tenet-hs' in f[2] else ('tenet-jvm (fixed)' if 'java' in f[2] else f[2][:30])))
            run2.append((nm, int(f[0]), int(f[1])))
    label = {'lean-kernel': "Lean's kernel", 'lean-kernel-paranoid': 'Lean paranoid', 'nanoda-32threads': 'nanoda, 32 threads',
             'tenet-hs': 'tenet-hs (Haskell)', 'tenet-jvm-compact': 'tenet-jvm, memory rework', 'tenet-jvm-compact-2': 'tenet-jvm, diagnostics run',
             'tenet-jvm-compact-3': 'tenet-jvm (fixed)'}
    lines += ['## Kernel race on the original proof: second machine, live', '',
              'A second AWS machine (`r7a.12xlarge`, 48 vCPU, 369 GB) checks the same 61.6 GB export of the original proof. '
              'Wall time is real time on a shared machine.', '',
              '| Checker | Verdict | Wall time | CPU | Peak memory |', '|---|:---:|---:|---:|---:|']
    for c in done2:
        if len(c) < 5: continue
        v = '✅ accepts' if c[1] == '0' else ('⏹ stopped by hand' if c[1] == '143' else ('❌ out of memory' if c[1] == '3' else f'exit {c[1]}'))
        lines.append(f"| {label.get(c[0], c[0])} | {v} | {c[2]} | {float(c[3] or 0):,.0f} s | {c[4]} GB |")
    def progress(nm):
        if 'tenet-jvm' in nm: return f"{jvm_count:,} of 1,468,414 declarations ({100 * jvm_count / 1468414:.0f}%)"
        if 'tenet-hs' in nm and posmap.get('tenet-hs-bin'): return f"{100 * posmap['tenet-hs-bin']:.1f}% through the file"
        if 'Lean' in nm: return 'whole file loaded, checking (no progress readout)'
        return ''
    for nm, et, rss in run2:
        lines.append(f"| {nm} | 🔵 checking: {progress(nm)} | {fmt_d(et / 60)} so far | | {rss / 1048576:.0f} GB now |")
    lines.append('')
    # the scoreboard at the top of README.md
    board = ['<!-- KERNELS:BEGIN -->', '| Checker | Written in | Result |', '|---|---|---|',
             '| **Tenet** | C# (mine) | ✅ accepts all 1,468,414 · 1 hour |']
    acc = {c[0]: c for c in done2 if len(c) >= 5}
    if 'nanoda-32threads' in acc and acc['nanoda-32threads'][1] == '0':
        board.append(f"| **nanoda** | Rust | ✅ accepts · {acc['nanoda-32threads'][2]} on 32 threads |")
    lang = {"Lean's kernel": "C++", 'Lean paranoid': 'C++', 'tenet-hs (Haskell)': 'Haskell (mine)', 'tenet-jvm (fixed)': 'Java (mine)'}
    for key, nm in (('lean-kernel', "Lean's kernel"), ('lean-kernel-paranoid', 'Lean paranoid'), ('tenet-hs', 'tenet-hs (Haskell)'), ('tenet-jvm-compact-3', 'tenet-jvm (fixed)')):
        if key in acc:
            c = acc[key]; board.append(f"| **{nm.split(' (')[0]}** | {lang[nm]} | {'✅ accepts · ' + c[2] if c[1] == '0' else '❌ exit ' + c[1]} |")
        else:
            r = next((x for x in run2 if x[0] == nm), None)
            board.append(f"| **{nm.split(' (')[0]}** | {lang[nm]} | 🔵 " + (f"{fmt_d(r[1] / 60)} in · {progress(nm)}" if r else 'waiting') + ' |')
    board += ['| con-leche, con-ron (Lean 4.36 bundle) | Lean | ⚪ decline: no support for one kind of type the proof uses |',
              '', f'<sub>Live, updated every few minutes · last update {now:%H:%M} UTC {now:%b %d}</sub>', '<!-- KERNELS:END -->']
    rp = os.path.join(repo, 'README.md'); rt = open(rp, encoding='utf-8').read()
    if '<!-- KERNELS:BEGIN -->' in rt:
        a = rt.index('<!-- KERNELS:BEGIN -->'); b = rt.index('<!-- KERNELS:END -->') + len('<!-- KERNELS:END -->')
        open(rp, 'w', encoding='utf-8').write(rt[:a] + '\n'.join(board) + rt[b:])

# ---------- step 5: the minified build
mb = T.get('minbuild')
if mb:
    frac = mb['done'] / mb['total'] if mb['total'] else 0
    state = ('✅ **built**' if 'exit status 0' in mb['result'] else '⚠️ **stopped**: ' + mb['result']) if mb['result'] else '🔵 **compiling**'
    if T.get('machine1_offline'): state = '⏸️ **paused**: the build machine is waiting for AWS Spot capacity'
    lines += ['## Step 5: building the smallest proof', '',
     f"The minified source, round {mb.get('round', '?')} ({mb.get('lines', 0):,} lines in {mb.get('files', 0):,} files, down from 17,374,242 lines in 175,188: see "
     '[docs/MINIFY.md](docs/MINIFY.md)) is compiling on the same machine, network cut off, in automatic repair rounds since '
     f"{mb['started']} UTC on 2026-11-22. When a round builds clean, its export is checked by Tenet first, then the other kernels.", '',
     f"{state} · `{bar(frac, 40)}` **{mb['done']:,}** of {mb['total']:,} Lake jobs ({100 * frac:.1f}%) · ❌ errors: **{mb['errors']}**", '',
     '| Round | Started (UTC) | Lines | Files | Errors | What changed |', '|---|---|---:|---:|---:|---|',
     '| round 1 | 06:19 | 13,850,849 | 30,698 | 5 | exact cut from the export; stopped: kept instances lost their dependencies |'] + [
     f"| {r['label']} | {r['start'][:5]} | {r['lines']:,} | {r['files']:,} | {r['errors']} | "
     + ({'round 2': 'keep what kept instances depend on; stopped: tactics name unused lemmas',
         'round 3': 'keep everything kept code mentions; built unmerged',
         'round 4': 'restore names the parser misread; automatic repair from here'}.get(r['label'], 'small files merged into bundles; any bundle that fails is taken apart' if r['label'].startswith('merged') else 'automatic repair of the previous round')) + ' |'
     for r in mb.get('rounds', [])] + ['',
     'Lake counts jobs, not files: the job total includes the already-built Mathlib and grows as Lake discovers work. '
     'An error here most likely means a declaration needed only while building a proof was cut; it goes back and the build resumes.', '']

# ---------- research on the export (tests run alongside the race)
RESEARCH = [
 ('1', 'Mutation test the kernels', 'Plant one fault at a time in a proof term and give every mutant to all six kernels. All should reject; any disagreement between kernels is a finding.',
  '🟢 **431 faults planted in 8 real slices of the proof (1.1M to 7.2M lines each), 2,583 kernel checks: all 6 kernels accepted every clean slice and rejected every fault.** No disagreements. (The last slice was cut short by a Spot interruption.)'),
 ('2', 'Where the checking time goes', 'The declarations that take most of the kernel time, from Tenet\'s per-declaration report.',
  '🟢 **0.3% of the declarations take half of the checking.** In Tenet\'s run, 4,335 declarations (of 1,468,414) took over 5 s each and add up to 128,568 CPU-seconds, 51% of its 252,006. 494 took over a minute, 22 over five minutes; the slowest, `CrystallineSemistableComparison.fc_range_le`, took 687 s. By area, p-adic Hodge theory dominates: `CrystallineSemistableComparison` 15% of the slow time and `GroundTheory.PAdicHodge` another 4%, then `GroundTheory.Arith` 7% and the étale cohomology parts. Reading the 61.6 GB file took 3,075 s of Tenet\'s 3,459 s wall time, overlapped with checking.'),
 ('3', 'Duplicate theorems', 'Theorems proved more than once with an identical statement, project vs Mathlib.',
  '🟢 **96,761 hand-named theorems repeat another theorem\'s statement exactly** (69,144 groups; equal up to bound-variable names; Lean\'s auto-generated helpers left out). Many are two proofs of the same named `Statement` proposition. For scale: 1,075,024 theorems are the project\'s own.'),
 ('4', 'The trusted base', 'What a person must read to trust the five STATEMENTS, as opposed to the 1.47M declarations of proof.',
  '🟢 first result: `riemannHypothesis` is stated with Mathlib\'s own definition only. `LFunction_eq_zero_re_of_isPrimitive` goes through a project-defined wrapper, `PrimitiveDirichletLZerosOnLine`, the kind of place a wrong definition could hide (Comparator\'s statement check covers it). Full count: the five statements rest on **4,915 declarations**, only **5** of them from the project (four statement wrappers and one helper); the other 4,910 are Mathlib and Lean.'),
 ('5', 'The spine and the hubs', 'The chain of declarations every dependency path must pass through (a dominator tree), and the most-used lemmas.',
  '🟢 **99.35% of the proof sits under one claim, `allChi`** (`UpperTheory.FinalTheorems.everyCharacter`). Below it: `everyCharacter_of_row` owns 77%, `every_character_of_literature_of_vWin` 67%, `every_character_of_theta_integrals_local_matching` 43%: the same chain traced by hand earlier, now measured. Top hub: `Formalism.BasicNotions.D7`, used directly by 155,523 declarations. Of the 1,468,414 declarations, 1,258,876 (86%) are the project\'s, holding 97% of the expression nodes.'),
 ('6', 'Haskell vs Lean per slice', 'tenet-hs and Lean\'s kernel timed on the same slices, matched by size, for a fair speed comparison.',
  '🔵 first slice, clean file, wall time with 24 checks running at once (so rough): nanoda 7.4 s, Tenet 9.8 s, Lean 11.4 s, Lean paranoid 14.8 s, **tenet-hs 16.8 s**, tenet-jvm 17.1 s. Fair timings, one at a time on an idle machine, come after the race.'),
]
lines += ['## Research on the export', '',
 'Six tests that only an exact export plus several independent kernels make possible. They run on the same machine, alongside the race, at no extra cost. '
 'None of them checks the mathematics: they are about the proof as an artifact, and about the checkers.', '',
 '| # | Test | What it shows | Status |', '|:---:|---|---|---|']
lines += [f'| {a} | **{b}** | {c} | {d_} |' for a, b, c, d_ in RESEARCH]
lines += ['']

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
 "- **00:43 and 00:44:** con-ron and con-leche **declined** in their default, formally verified mode: the proof uses a reflexive inductive type (`FunctorialResolution.EmbeddedResolution.PrincipalizationCertificate`), which their verified model doesn't cover. That is not a rejection of the proof. Both were restarted at 00:45 in trusted mode, which runs every check the official kernel does.",
 "- **00:50 and 00:52:** both declined again in trusted mode, at the same type. So con-leche and con-ron don't support reflexive inductive types in either mode; they give no verdict on this proof.",
 "- **03:08:** Tenet stopped after checking **1,468,255 of 1,468,414 declarations, 0 failed**: it ran out of memory on the last 159. The cause was the race setup, not Tenet or the proof: its sandbox was capped at 120 GB, and .NET limits its heap to 75% of that (peak 89.7 GB). Rerun from 03:16 with a 320 GB cap.",
 "- **05:37 to 05:46:** a fifth Spot interruption. It stopped the four checkers still running: Lean's kernel (about 6 h in), paranoid mode, nanoda and tenet-hs, with no verdicts. Everything on disk was kept. The race is not restarted for now; the machine now builds the minified proof, which Tenet will check, and the other kernels after that.",
 "- **2026-11-23 07:02: tenet-jvm accepts the whole proof** (fixed build, branch `jvm-compact-memory` 53cf8a4): all declarations verified, 1,484,729 constants and 7,969 inductive blocks, axioms only `propext`, `Quot.sound`, `Classical.choice`; 6 h 05 m wall, 26,202 CPU-seconds, 96.4 GB peak. The fix: cache definitional-equality failures, which turned one theorem from a 104 GB hang into 373 ms.",
 "- **2026-11-22 23:28: nanoda accepts the whole proof** on the second machine: exit 0, 2 h 42 m on 32 threads, 79.4 GB peak (sharing the machine with four other kernels).",
 "- **22:31:** a memory-reworked tenet-jvm (branch `jvm-compact-memory`) ran out of memory at its 120 GB cap after 49 min, at the same declaration as before (`...FormalGroupSystem.Pf.ea_card_img._simp_1_1`): one pathological declaration, not general footprint. Being narrowed down.",
 "- **2026-11-22 20:46:** a second machine (`r7a.12xlarge`, 48 vCPU, 369 GB, Spot), made from the 20:19 snapshot, restarts the race for the four kernels the interruptions stopped: Lean's kernel, paranoid mode, nanoda (now with 32 threads) and tenet-hs, all four in parallel on the same export. The first machine keeps building the smallest proof.",
 "- **04:16:55: Tenet accepts the whole proof.** All 1,468,414 declarations checked, 0 failed, exit 0, in 1 h 0 m 27 s (peak 236 GB). Tenet is an independent Lean kernel written from scratch in C#, and the first of the from-scratch kernels to finish.",
 "- **03:17:** tenet-jvm stopped by hand. It had been stuck for about 90 minutes reading one declaration (`Formalism.MainNotions.FormalGroupSystem.Pf.ea_card_img._simp_1_1`) while its memory grew to 258 GB. Recorded as stalled, not as a verdict; to be reproduced on a small export of that lemma.",
 "- **00:38:** switched to a parallel race. Each checker uses one core, so the other seven now run alongside Lean's kernel instead of after it, each in its own memory-capped sandbox. Same hourly cost, results hours sooner.", '',
 '</details>', '',
 'Rate and finish come from the last hour of the timestamped build log. Build it yourself: [docs/BUILD-ORIGINAL.md](docs/BUILD-ORIGINAL.md).']
open(os.path.join(repo, 'BUILD-STATUS.md'), 'w').write('\n'.join(lines) + '\n')

# ---------- the live counter at the top of README.md (between the STATUS markers)
def readme_counter():
    mb = T.get('minbuild') or {}
    if not mb.get('lines'): return
    ORIG_L, ORIG_F = 17374242, 175188
    L, F = mb['lines'], mb['files']
    bf, sf = mb.get('built_files', 0), mb.get('src_files', 1) or 1
    clean = mb.get('result') and 'exit status 0' in mb['result'] and mb.get('errors', 1) == 0
    state = '✅ BUILT' if clean else ('🔁 REPAIRING' if mb.get('errors') else '🔵 BUILDING')
    if T.get('machine1_offline'): state = '⏸️ PAUSED: the build machine is waiting for AWS Spot capacity (numbers are its last reading)'
    cell = lambda label, big, small: f'<td align="center" width="20%"><sub><b>{label}</b></sub><h2>{big}</h2><sub>{small}</sub></td>'
    T0 = datetime.datetime(2026, 11, 22, 6, 19, 37)                      # the first minified build
    t_end = datetime.datetime.utcfromtimestamp(mb['log_mtime']) if clean and mb.get('log_mtime') else now
    el = (t_end - T0).total_seconds() / 60
    elapsed = f'{int(el // 60)}h {int(el % 60):02d}m'
    nrounds = len(mb.get('rounds', [])) + 1
    block = ['<!-- STATUS:BEGIN -->', '<div align="center">', '',
      f'**The smallest proof, live** · round {mb.get("round", "?")} · {state} · updated {now:%H:%M} UTC {now:%b %d}', '',
      '<table><tr>',
      cell('SMALLER', f'{100 * (1 - L / ORIG_L):.1f}%', 'in lines, so far'),
      cell('LINES', f'{L / 1e6:.2f}M', f'was {ORIG_L / 1e6:.2f}M'),
      (cell('FILES', f'{F:,}', f'was {ORIG_F:,}') if F < 100000 else
       cell('FILES', '~32,000', f'was {ORIG_F:,} · after small files are merged')),
      cell('THIS ROUND', f'{100 * bf / sf:.0f}% built', f'{bf:,} of {sf:,} files · {mb.get("errors", 0)} errors to repair'),
      cell('TIME', elapsed, f'{"to a clean build" if clean else "and counting"} · since the first build, 06:19 UTC Nov 22 · {nrounds} rounds'),
      '</tr></table>', '',
      '<sub>Not confirmed until a round builds with 0 errors. Each round keeps what the last one\'s build said was missing, '
      'so the percentage can only go down from here. Updated every 2 minutes from the build machine. '
      '<a href="docs/MINIFY.md#log">Log of every round</a></sub>', '', '</div>', '<!-- STATUS:END -->']
    for rel, link in (('README.md', 'docs/MINIFY.md#log'), ('docs/MINIFY.md', '#log')):
        rp = os.path.join(repo, rel); t = open(rp, encoding='utf-8').read()
        if '<!-- STATUS:BEGIN -->' in t:
            a = t.index('<!-- STATUS:BEGIN -->'); b = t.index('<!-- STATUS:END -->') + len('<!-- STATUS:END -->')
            t = t[:a] + '\n'.join(block).replace('href="docs/MINIFY.md#log"', f'href="{link}"') + t[b:]
            open(rp, 'w', encoding='utf-8').write(t)
readme_counter()

print(f'{built} built, {pct:.1f}%, rate {rate:.0f}/min, finish {eta:%H:%M} UTC' if eta else f'{built} built')
