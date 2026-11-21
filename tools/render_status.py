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
STOPPED_H = 0.3                                            # Spot interruption 02:06 to 02:12, not billed
cost = ((now - LAUNCH).total_seconds() / 3600 - STOPPED_H) * PRICE
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
head = '✅ **Finished**' if done and 'exit status 0' in T['result'] else ('⚠️ **Stopped**' if done else '🟢 **Compiling**')
lines = [
 '# Live: building the claimed Lean proof of the Riemann Hypothesis', '',
 f'{head}: the original proof, all 175,187 files, on one AWS machine. Updated every 10 minutes; '
 f'last update **{now:%Y-%m-%d %H:%M} UTC**.', '',
 f'## {pct:.1f}% built', '',
 f'`{bar(built / TOTAL, 40)}`  **{built:,}** of 175,187 proof files', '',
 '| ⏱ Time left | 🏁 Finish (UTC) | ⚡ Rate | 💵 Spent | 💵 Projected total | ❌ Errors |',
 '|:---:|:---:|:---:|:---:|:---:|:---:|',
 f"| {fmt_d(left_min) if left_min else '?'} | {eta.strftime('%H:%M') if eta else '?'} | {rate:.0f} files/min | ${cost:.2f} | ${cost_end:.0f} | {T['errors']} |", '',
 f'![Proof files compiled over time](docs/status/{chart_name})', '',
 '## By library', '',
 '| Library | Built | Progress |', '|---|---:|---|']
for name, tot in LIBS:
    b = T['lib'].get(name, 0)
    lines.append(f'| `{name}` | {b:,} / {tot:,} | `{bar(min(b / tot, 1), 20)}` {100 * b / tot:.0f}% |')
lines += ['', '## The machine', '',
 '| | |', '|---|---|',
 '| Instance | AWS `m6a.48xlarge` Spot, Ohio, about $1.56/hour |',
 f"| CPUs | 192 vCPUs (96 cores), load {T['load']:.0f}, {T['lean_procs']} Lean processes running |",
 f"| Memory | {T['mem_used_gb']:.0f} GB used of {T['mem_total_gb']:.0f} GB |",
 f"| Disk | {T['disk_free_gb']:.0f} GB free of {T['disk_total_gb']:.0f} GB |",
 '| Sandbox | bubblewrap: no network, everything read-only except the build folder |',
 '| Safety net | the disk survives termination, and is snapshotted every 2 hours |', '',
 '## Just compiled', '']
lines += [f'- `{m}`' for m in reversed(T['recent'])]
race_tsv = T.get('race', {}).get('tsv', '')
if race_tsv.strip():
    lines += ['', '## Kernel race on the exact export', '', '| Checker | Verdict | Wall time | CPU (user) | Peak memory |', '|---|:---:|---:|---:|---:|']
    for row in race_tsv.strip().split('\\n')[1:]:
        c = row.split('\\t')
        if len(c) >= 6:
            lines.append(f"| {c[0]} | {'✅ accepts' if c[1] == '0' else '❌ exit ' + c[1]} | {c[2]} | {c[3]} s | {c[5]} GB |")
lines += ['', '## What happens when it finishes', '',
 '**Queued on the machine; it starts by itself when the build succeeds:**', '',
 '1. **Exact reduced form.** Export the five theorems with `lean4export`. The export holds exactly the declarations the proof uses, measured by Lean itself, not guessed.',
 "2. **Kernel race.** Check that one export, one checker at a time, each timed with peak memory recorded: Lean's kernel, its paranoid mode, nanoda, con-leche, con-ron, and the three clean-room kernels **Tenet** (C#), **tenet-hs** (Haskell) and **tenet-jvm**. All eight accepted a test export of the same format.",
 "3. **Axioms.** List exactly which axioms the five theorems depend on.",
 '4. **Publish** the times, the verdicts and the exact size here.', '',
 '## Log', '',
 "- **2026-11-20 23:29 UTC:** started compiling the original proof, after the source-level reduction turned out to drop real dependencies ([why](README.md)).",
 "- **00:39 to 00:49:** disk full. Lake's per-module `.setup.json` files reached 92 GB (about 4.6 MB each, listing every import). They are now deleted as modules finish; nothing built was lost.",
 "- **01:45:** status counter fixed. Lake re-prints warnings for modules already built, which the old counter counted twice.",
 "- **02:06 to 02:12:** AWS reclaimed the Spot machine. It stopped with its disk kept, and came back on its own when capacity returned; the build resumed with nothing lost. Everything now restarts by itself after any interruption, and progress is counted from compiled files on disk.",
 "- **2026-11-21 09:21 to 09:24:** a second Spot interruption. The machine resumed the build by itself within a minute of coming back.",
 "- **10:25 to 10:34:** a third Spot interruption, with no capacity for 9 minutes. Resumed by itself again; nothing lost.", '',
 'Rate and finish come from the last hour of the timestamped build log. Build method: [docs/BUILD.md](docs/BUILD.md).']
open(os.path.join(repo, 'BUILD-STATUS.md'), 'w').write('\n'.join(lines) + '\n')
print(f'{built} built, {pct:.1f}%, rate {rate:.0f}/min, finish {eta:%H:%M} UTC' if eta else f'{built} built')
