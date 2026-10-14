import os,sys,json,base64
OUT,DEL=sys.argv[1],sys.argv[2]
S=json.load(open(f"{OUT}/matched350_summary.json"))
def b64(fn):
    with open(f"{OUT}/{fn}","rb") as f: return "data:image/png;base64,"+base64.b64encode(f.read()).decode()
order=["A","C","B"]
def cc(v): return "good" if v>80 else ("warn" if v>40 else "bad")
rows="".join(f"<tr><td style='text-align:left'>{S[c]['name']}</td><td>{S[c]['mean']:.1f}</td><td>{S[c]['ret']:.1f}</td>"
             f"<td>{S[c]['cool']:.1f}</td><td>{S[c]['Tstd']:.2f}</td><td>{S[c]['ADPI']:.0f}</td>"
             f"<td class='{cc(S[c]['cov'])}'>{S[c]['cov']:.0f}%</td><td>{S[c]['lag']:.1f}</td></tr>" for c in order)
def pccard(c):
    d=S[c]
    return (f"<div class=pc><h3>{d['name']}</h3><img src='{b64(f'render_{c}.png')}'>"
            f"<div class=kv><span>mean <b>{d['mean']:.1f}°C</b></span><span>exit <b>{d['ret']:.1f}°C</b></span>"
            f"<span>cooling out <b>{d['cool']:.1f} kW</b></span><span>coverage <b>{d['cov']:.0f}%</b></span></div>"
            f"<img src='{b64(f'{c}_T_plane.png')}'><img src='{b64(f'{c}_T_slice.png')}'></div>")
html=f"""<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>Cassette Diffuser — Setpoint Study</title><style>
:root{{--bg:#f6f8fb;--card:#fff;--ink:#0f172a;--mut:#64748b;--line:#e2e8f0;--accent:#2563eb}}
@media(prefers-color-scheme:dark){{:root:not([data-theme=light]){{--bg:#0f172a;--card:#1e293b;--ink:#e2e8f0;--mut:#94a3b8;--line:#334155}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 -apple-system,Segoe UI,Roboto,sans-serif}}
header{{padding:20px 16px;max-width:1000px;margin:auto}}h1{{font-size:20px;margin:0 0 4px}}.sub{{color:var(--mut);font-size:12.5px}}
nav{{position:sticky;top:0;background:var(--bg);border-bottom:1px solid var(--line);padding:0 10px;display:flex;gap:2px;flex-wrap:wrap;max-width:1000px;margin:auto;z-index:5}}
nav button{{background:none;border:0;padding:12px 12px;color:var(--mut);font:inherit;font-weight:600;cursor:pointer;border-bottom:2px solid transparent}}
nav button.on{{color:var(--accent);border-bottom-color:var(--accent)}}
main{{max-width:1000px;margin:auto;padding:16px}}section{{display:none}}section.on{{display:block}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px;margin:0 0 16px}}
img{{max-width:100%;border-radius:8px;display:block;margin:8px 0}}
.finding{{border-left:4px solid #dc2626;padding:12px 14px;background:color-mix(in srgb,#dc2626 7%,var(--card))}}
.eq{{border-left:4px solid #16a34a;padding:12px 14px;background:color-mix(in srgb,#16a34a 7%,var(--card))}}
table{{width:100%;border-collapse:collapse;font-size:13px}}th,td{{padding:8px 6px;text-align:center;border-bottom:1px solid var(--line)}}
th{{background:#1e3a5f;color:#fff}}td.good{{color:#16a34a;font-weight:700}}td.warn{{color:#d97706;font-weight:700}}td.bad{{color:#dc2626;font-weight:700}}
.pc{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px;margin-bottom:16px}}
.kv{{display:flex;gap:16px;flex-wrap:wrap;color:var(--mut);font-size:13px;margin:6px 0}}.kv b{{color:var(--ink)}}
.note{{color:var(--mut);font-size:13px}}h3{{margin:.2em 0}}code{{background:var(--line);padding:1px 5px;border-radius:4px}}
</style></head><body>
<header><h1>Ceiling-Cassette Diffuser — Setpoint Comparison</h1>
<div class=sub>12×10×4 m hall · two 4-way cassettes · identical airflow 1.81 m³/s · 14 °C supply · 12 kW load · buoyantPimpleFoam · matched snapshot at t = 350 s</div></header>
<nav><button class=on onclick="go(0,this)">Overview</button><button onclick="go(1,this)">Trajectory</button>
<button onclick="go(2,this)">Exit flow</button><button onclick="go(3,this)">Coverage</button><button onclick="go(4,this)">Per-case</button><button onclick="go(5,this)">Method</button></nav>
<main>
<section class=on>
<div class="card finding"><b>Key finding.</b> All three remove the same air mass and reach the same exit-air equilibrium (19.4 °C, 12 kW) by energy balance — they differ in <i>how</i> the air is used. The <b>baseline</b> mixes supply into the room, exhausts warm, and holds 24 °C with 89% comfort coverage. <b>Swirl</b> and <b>steep</b> short-circuit cold supply back to the return, so at a matched 350 s the room is 3–4 °C warmer, coverage collapses (swirl 4%), and they head toward a hotter, slower equilibrium.</div>
<div class=card><h3>Matched comparison @ t = 350 s</h3>
<table><tr><th>Pattern</th><th>Mean °C</th><th>Exit °C</th><th>Cooling kW</th><th>Tstd</th><th>ADPI</th><th>Coverage</th><th>Lag °C</th></tr>{rows}</table>
<p class=note><b>ADPI caveat:</b> ADPI is relative to the local mean, so swirl's uniformly-too-warm, calm zone scores highest ADPI (82) with the lowest real coverage (4%). Judge on absolute coverage + cooling removed.</p></div>
<div class=card><img src="{b64('cmp_bars_matched.png')}"></div>
<div class="card eq"><b>Equilibrium (energy balance).</b> At steady state the exhaust must satisfy <code>Q = ṁ·cp·(T_exit − T_supply)</code> → <code>T_exit = 14 + 12000/(2.227·1004) = 19.4 °C</code> for <b>all three</b>, removing the full 12 kW. The patterns differ only in how fast they get there and how hot the occupied zone sits meanwhile — baseline by ~185 s, swirl still climbing (31.5 °C at 806 s).</div>
</section>
<section><div class=card><h3>Room temperature vs time</h3><img src="{b64('cmp_trajectory_set.png')}">
<p class=note>Solid = occupied/volume mean, dotted = exit/return. Baseline flattens at setpoint by ~185 s; swirl and steep keep climbing toward hotter equilibria (very long time-constant — a thermostat or occupants would react long before).</p></div></section>
<section><div class=card><h3>Exit (return) flow — the mechanism</h3><img src="{b64('exit_return_trajectory.png')}">
<p class=note>The exit temperature <i>is</i> the cooling delivered: Q = ṁ·cp·(T_exit − 14). Baseline exhausts warm (19 °C → 11.6 kW); swirl/steep exhaust cold (17 °C → ~8 kW) because cold supply short-circuits to the return.</p>
<img src="{b64('exit_near_return_slice.png')}">
<p class=note>Near-ceiling slice through the cassettes: in swirl/steep the blue (cold) air curls straight back into the central return; in baseline the returning air is warmer, having mixed with the room first.</p></div></section>
<section><div class=card><h3>Comfort coverage @1.1 m</h3><img src="{b64('cmp_coverage_panel.png')}">
<p class=note>Green = within comfort band (23–26 °C, V&lt;0.35 m/s), red = outside. Baseline fills the plan; steep leaves gaps; swirl is almost entirely out of band at 350 s.</p></div></section>
<section>{''.join(pccard(c) for c in order)}</section>
<section><div class=card><h3>Model</h3><p>OpenFOAM v2012 buoyantPimpleFoam (transient, compressible), k-ω SST, 576k cells, 4-core parallel. Hall 480 m³; two 0.6×0.6 m 4-way cassettes.</p>
<h3>Controlled variable</h3><p>Identical inlet area 0.64 m² and vertical supply −2.83 m/s → identical airflow 1.81 m³/s and mass flow 2.23 kg/s (mass conserved to ~1e-10). Only the horizontal throw direction differs.</p>
<h3>Why the mean differs</h3><p>Open system: <code>dU/dt = Q − ṁ·cp·(T_exit − T_supply)</code>. Q, ṁ, T_supply identical, so the only difference is the exit temperature — set by the flow pattern. Lower exit T (short-circuit) → less heat carried out → warmer room.</p>
<h3>Caveats</h3><p class=note>Matched snapshot at t = 350 s. Baseline is at steady state; swirl & steep are still approaching a hotter equilibrium (not force-converged). Single mesh (576k); RANS turbulence.</p></div></section>
</main>
<script>function go(i,b){{document.querySelectorAll('section').forEach((s,j)=>s.classList.toggle('on',j==i));document.querySelectorAll('nav button').forEach(x=>x.classList.remove('on'));b.classList.add('on');window.scrollTo(0,0);}}</script>
</body></html>"""
open(f"{DEL}/hall_diffuser_setpoint_dashboard.html","w",encoding="utf-8").write(html)
print("HTML rebuilt:",os.path.getsize(f"{DEL}/hall_diffuser_setpoint_dashboard.html"),"bytes")
