import os,sys,json,base64
OUT,DEL=sys.argv[1],sys.argv[2]
S=json.load(open(f"{OUT}/comparison_summary.json"))
def b64(fn):
    with open(f"{OUT}/{fn}","rb") as f: return "data:image/png;base64,"+base64.b64encode(f.read()).decode()
order=["A","C","B"]
rows="".join(f"<tr><td style='text-align:left'>{S[c]['name']}</td><td>{S[c]['mean']:.1f}</td><td>{S[c]['ret']:.1f}</td>"
             f"<td>{S[c]['lag']:.1f}</td><td>{S[c]['Tstd']:.2f}</td><td>{S[c]['ADPI']:.0f}</td>"
             f"<td class='{'good' if S[c]['comfort_cov']>80 else ('warn' if S[c]['comfort_cov']>40 else 'bad')}'>{S[c]['comfort_cov']:.0f}%</td>"
             f"<td>{S[c]['mean_slope_Cmin']:+.2f}</td><td>{'✓' if S[c]['equilibrated'] else '—'}</td></tr>" for c in order)
def card(c):
    d=S[c]
    return (f"<div class='pc'><h3>{d['name']}</h3>"
            f"<img src='{b64(f'render_{c}.png')}'><div class='kv'>"
            f"<span>Mean <b>{d['mean']:.1f}°C</b></span><span>Return <b>{d['ret']:.1f}°C</b></span>"
            f"<span>Coverage <b>{d['comfort_cov']:.0f}%</b></span><span>ADPI <b>{d['ADPI']:.0f}</b></span></div>"
            f"<img src='{b64(f'{c}_T_plane.png')}'><img src='{b64(f'{c}_T_slice.png')}'></div>")
html=f"""<!doctype html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Cassette Diffuser — Setpoint Study</title><style>
:root{{--bg:#f6f8fb;--card:#fff;--ink:#0f172a;--mut:#64748b;--line:#e2e8f0;--accent:#2563eb}}
:root:not([data-theme=light]) @media(prefers-color-scheme:dark){{}}
@media(prefers-color-scheme:dark){{:root:not([data-theme=light]){{--bg:#0f172a;--card:#1e293b;--ink:#e2e8f0;--mut:#94a3b8;--line:#334155}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 -apple-system,Segoe UI,Roboto,sans-serif}}
header{{padding:22px 16px;max-width:1000px;margin:auto}}h1{{font-size:21px;margin:0 0 4px}}.sub{{color:var(--mut);font-size:13px}}
nav{{position:sticky;top:0;background:var(--bg);border-bottom:1px solid var(--line);padding:0 16px;display:flex;gap:4px;flex-wrap:wrap;max-width:1000px;margin:auto;z-index:5}}
nav button{{background:none;border:0;padding:12px 14px;color:var(--mut);font:inherit;font-weight:600;cursor:pointer;border-bottom:2px solid transparent}}
nav button.on{{color:var(--accent);border-bottom-color:var(--accent)}}
main{{max-width:1000px;margin:auto;padding:16px}}section{{display:none}}section.on{{display:block}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px;margin:0 0 16px}}
img{{max-width:100%;border-radius:8px;display:block;margin:8px 0}}
.finding{{border-left:4px solid #dc2626;padding:12px 14px;background:color-mix(in srgb,#dc2626 7%,var(--card))}}
table{{width:100%;border-collapse:collapse;font-size:13.5px}}th,td{{padding:8px 6px;text-align:center;border-bottom:1px solid var(--line)}}
th{{background:#1e3a5f;color:#fff}}td.good{{color:#16a34a;font-weight:700}}td.warn{{color:#d97706;font-weight:700}}td.bad{{color:#dc2626;font-weight:700}}
.pc{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px;margin-bottom:16px}}
.kv{{display:flex;gap:16px;flex-wrap:wrap;color:var(--mut);font-size:13px;margin:6px 0}}.kv b{{color:var(--ink)}}
.note{{color:var(--mut);font-size:13px}}h3{{margin:.2em 0}}
</style></head><body>
<header><h1>Ceiling-Cassette Diffuser — Setpoint Comparison</h1>
<div class=sub>12×10×4 m hall · two 4-way cassettes · identical airflow (1.81 m³/s) · 12 kW load · OpenFOAM buoyantPimpleFoam · k-ω SST</div></header>
<nav><button class=on onclick="go(0,this)">Overview</button><button onclick="go(1,this)">Trajectory</button>
<button onclick="go(2,this)">Coverage</button><button onclick="go(3,this)">Per-case</button><button onclick="go(4,this)">Method</button></nav>
<main>
<section class=on><div class="card finding"><b>Key finding.</b> At identical airflow and load, only the <b>baseline 4-way</b> pattern conditions the occupied zone — it holds setpoint (24.4 °C, 89% comfort coverage). <b>Swirl</b> and <b>steep</b> short-circuit (supply loops back to the return before reaching the room), so the occupied zone runs away warm — swirl worst at 4% coverage. The diffuser <b>pattern</b>, not the airflow, decides whether the AC reaches every corner.</div>
<div class=card><h3>Scoreboard</h3><table><tr><th>Pattern</th><th>Mean °C</th><th>Return °C</th><th>Lag °C</th><th>Tstd</th><th>ADPI</th><th>Coverage</th><th>Slope °C/min</th><th>Equil?</th></tr>{rows}</table>
<p class=note><b>ADPI caveat:</b> ADPI is computed relative to the <i>local</i> mean, so swirl's uniformly-too-warm, dead-calm zone scores the <i>highest</i> ADPI (82) while giving the <i>lowest</i> real comfort coverage (4%). Rank on absolute comfort coverage, not ADPI alone.</p></div>
<div class=card><img src="{b64('cmp_bars_set.png')}"></div></section>
<section><div class=card><h3>Room temperature vs time</h3><img src="{b64('cmp_trajectory_set.png')}">
<p class=note>Solid = occupied/volume mean, dotted = return air. The baseline flattens at setpoint; swirl and steep keep climbing (not yet equilibrated — their true steady state is hotter still). Return air pinned low on swirl/steep is the short-circuit signature.</p></div></section>
<section><div class=card><h3>Comfort coverage @1.1 m</h3><img src="{b64('cmp_coverage_panel.png')}">
<p class=note>Green = within comfort band (23–26 °C, V&lt;0.35 m/s), red = outside. Baseline fills the plan; steep leaves gaps; swirl is almost entirely out of band.</p>
<p class=note><b>Mechanism —</b> baseline's strong radial throw spreads air along the ceiling and drops it into the room before it can return; swirl's tangential jets rotate straight back into the central return (return 16.8 °C); steep's weak horizontal throw lets the cold column be drawn back up by the adjacent return. Short-circuit lag (mean−return): 5.2 / 9.5 / 11.1 °C.</p></div></section>
<section>{''.join(card(c) for c in order)}</section>
<section><div class=card><h3>Model</h3><p>OpenFOAM v2012 buoyantPimpleFoam (transient, compressible, perfect gas), k-ω SST, 576,000 cells, 4-core parallel. Hall 480 m³, two 0.6×0.6 m 4-way cassettes (central 0.4×0.4 return + 4 supply slots).</p>
<h3>Controlled variable</h3><p>All patterns keep the same vertical supply component (−2.83 m/s) → identical airflow 1.81 m³/s (~13.6 ACH). Only horizontal throw differs: baseline radial, swirl tangential, steep reduced-throw.</p>
<h3>Load & validation</h3><p>Supply 14 °C, adiabatic walls, 12 kW sensible load (~100 W/m²), uniform-24 °C start. Energy balance validated: baseline return 19.2 °C vs 19.5 °C from Q=ṁ·cp·ΔT.</p>
<h3>Caveats</h3><p class=note>Baseline reached statistical steady state; swirl & steep were still warming at t=350 s, so their coverage here is an optimistic upper bound. Single mesh (576k) — mesh-independence pending. RANS turbulence (modelled, not resolved).</p>
<h3>Next steps</h3><p class=note>Optional full-equilibrium runs for swirl/steep; mesh-independence on the baseline; an under-sized-airflow case to map the coverage vs ACH trade-off.</p></div></section>
</main>
<script>function go(i,b){{document.querySelectorAll('section').forEach((s,j)=>s.classList.toggle('on',j==i));document.querySelectorAll('nav button').forEach(x=>x.classList.remove('on'));b.classList.add('on');window.scrollTo(0,0);}}</script>
</body></html>"""
open(f"{DEL}/hall_diffuser_setpoint_dashboard.html","w",encoding="utf-8").write(html)
print("HTML ->",f"{DEL}/hall_diffuser_setpoint_dashboard.html",os.path.getsize(f"{DEL}/hall_diffuser_setpoint_dashboard.html"),"bytes")
