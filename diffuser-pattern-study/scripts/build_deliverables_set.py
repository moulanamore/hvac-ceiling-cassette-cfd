import os,sys,json,base64
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
OUT,DEL=sys.argv[1],sys.argv[2]
S=json.load(open(f"{OUT}/comparison_summary.json"))
order=["A","C","B"]  # best -> worst by coverage
def img(ax,fn):
    ax.imshow(plt.imread(fn)); ax.axis("off")
def textpage(pdf,title,lines,fs=11):
    fig=plt.figure(figsize=(8.27,11.69)); fig.text(0.08,0.93,title,fontsize=17,weight="bold",color="#0f172a")
    y=0.87
    for ln in lines:
        w="bold" if ln.startswith("##") else "normal"
        t=ln[2:].strip() if ln.startswith("##") else ln
        col="#0f172a" if w=="bold" else "#1f2937"
        fig.text(0.08,y,t,fontsize=fs+2 if w=="bold" else fs,weight=w,color=col,wrap=True); y-=0.035 if w=="bold" else 0.028
    pdf.savefig(fig); plt.close(fig)

pdf=PdfPages(f"{DEL}/hall_diffuser_setpoint_report.pdf")
# P1 title + finding + trajectory
fig=plt.figure(figsize=(8.27,11.69))
fig.text(0.08,0.95,"Ceiling-Cassette Diffuser Study — Setpoint Comparison",fontsize=16,weight="bold",color="#0f172a")
fig.text(0.08,0.925,"12×10×4 m hall · two 4-way cassettes · identical airflow · 12 kW load · OpenFOAM buoyantPimpleFoam",fontsize=9.5,color="#475569")
fig.text(0.08,0.895,"KEY FINDING",fontsize=12,weight="bold",color="#b91c1c")
kf=("At identical airflow and cooling load, only the BASELINE 4-way pattern conditions the occupied zone: it holds the\n"
"setpoint (24.4 °C mean, 89% comfort coverage). The SWIRL and STEEP variants short-circuit — supply air loops\n"
"back to the central return before reaching the room — so the occupied zone runs away warm (swirl worst: 4% coverage).\n"
"Diffuser pattern, not airflow, decides whether the AC 'reaches every corner'.")
fig.text(0.08,0.80,kf,fontsize=10.5,color="#0f172a")
ax=fig.add_axes([0.07,0.08,0.86,0.60]); img(ax,f"{OUT}/cmp_trajectory_set.png")
pdf.savefig(fig); plt.close(fig)
# P2 bars + table
fig=plt.figure(figsize=(8.27,11.69)); fig.text(0.08,0.95,"Quantitative comparison",fontsize=15,weight="bold")
ax=fig.add_axes([0.06,0.60,0.88,0.30]); img(ax,f"{OUT}/cmp_bars_set.png")
rows=[["Pattern","Mean °C","Return °C","Lag °C","Tstd","ADPI","Coverage","Slope °C/min","Equil?"]]
for c in order:
    d=S[c]; rows.append([d["name"],f"{d['mean']:.1f}",f"{d['ret']:.1f}",f"{d['lag']:.1f}",f"{d['Tstd']:.2f}",
        f"{d['ADPI']:.0f}",f"{d['comfort_cov']:.0f}%",f"{d['mean_slope_Cmin']:+.2f}","yes" if d['equilibrated'] else "no"])
axt=fig.add_axes([0.05,0.30,0.9,0.22]); axt.axis("off")
tb=axt.table(cellText=rows,loc="center",cellLoc="center"); tb.auto_set_font_size(False); tb.set_fontsize(8.5); tb.scale(1,1.6)
for j in range(len(rows[0])): tb[0,j].set_facecolor("#1e3a5f"); tb[0,j].set_text_props(color="white",weight="bold")
fig.text(0.08,0.26,"ADPI caveat:",fontsize=10,weight="bold",color="#b45309")
fig.text(0.08,0.235,"ADPI measures uniformity & draft relative to the LOCAL mean, so swirl's uniformly-too-warm, dead-calm zone\nscores highest ADPI (82) while delivering the lowest real comfort coverage (4%). Rank on absolute coverage, not ADPI alone.",fontsize=9.5,color="#0f172a")
pdf.savefig(fig); plt.close(fig)
# P3 coverage panel + mechanism
fig=plt.figure(figsize=(8.27,11.69)); fig.text(0.08,0.95,"Comfort coverage & short-circuit mechanism",fontsize=15,weight="bold")
ax=fig.add_axes([0.04,0.62,0.92,0.28]); img(ax,f"{OUT}/cmp_coverage_panel.png")
mech=("Why the patterns differ (same airflow, same load):\n"
"• Baseline 45° down-and-out — strong radial throw spreads supply air along the ceiling, it entrains and drops into\n"
"   the occupied zone before reaching the central return. Good penetration → room conditioned, return warms to 19.2 °C.\n"
"• Swirl (tangential slots) — sets up a rotating near-ceiling layer that feeds straight back into the central return.\n"
"   Cold air short-circuits (return 16.8 °C); the occupied zone is starved and heats up. Worst coverage (4%).\n"
"• Steep (weak horizontal throw) — the cold column drops near the cassette and part is drawn back up by the adjacent\n"
"   return; limited lateral spread. Partial coverage (68%), still warming.\n\n"
"Short-circuit lag (occupied mean − return) is the diagnostic: 5.2 °C baseline, 9.5 °C steep, 11.1 °C swirl.")
fig.text(0.08,0.30,mech,fontsize=10,color="#0f172a")
pdf.savefig(fig); plt.close(fig)
# P4 per-case renders
fig=plt.figure(figsize=(8.27,11.69)); fig.text(0.08,0.95,"Flow structure — 3D streamlines from the 8 supply slots",fontsize=14,weight="bold")
for i,c in enumerate(["A","B","C"]):
    ax=fig.add_axes([0.06,0.66-0.30*i,0.6,0.27]); img(ax,f"{OUT}/render_{c}.png")
    fig.text(0.70,0.80-0.30*i,f"{S[c]['name']}",fontsize=11,weight="bold")
    fig.text(0.70,0.77-0.30*i,f"mean {S[c]['mean']:.1f} °C\nreturn {S[c]['ret']:.1f} °C\ncoverage {S[c]['comfort_cov']:.0f}%",fontsize=9.5)
pdf.savefig(fig); plt.close(fig)
# P5 methodology
textpage(pdf,"Methodology & caveats",[
"## Model",
"OpenFOAM v2012 buoyantPimpleFoam (transient, compressible, perfect gas), k-ω SST, 576,000 cells.",
"Hall 12×10×4 m (480 m³). Two 0.6×0.6 m 4-way cassettes at (3,5) and (9,5): central 0.4×0.4 return + 4 supply slots.",
"",
"## Controlled variable",
"All three patterns keep the SAME vertical supply component (−2.83 m/s) → identical airflow 1.81 m³/s (~13.6 ACH).",
"Only the horizontal throw direction/magnitude differs: baseline radial, swirl tangential, steep reduced-throw.",
"",
"## Boundary / load",
"Supply 14 °C; adiabatic walls; 12 kW sensible load (scalarSemiImplicitSource, ~100 W/m²); uniform-24 °C start.",
"Energy balance validated: baseline return settles at 19.2 °C vs 19.5 °C predicted by Q = ṁ·cp·ΔT.",
"4-core parallel (hierarchical 2×2×1); return/mean monitored each step; fields time-averaged over the window.",
"",
"## Caveats",
"• Baseline reached statistical steady state (slope ≈0). Swirl and steep were still warming at t=350 s —",
"   their TRUE equilibrium is hotter still, so their coverage shown here is an optimistic upper bound.",
"• Single mesh (576k). Mesh-independence check pending.",
"• RANS (steady-in-the-mean turbulence); large-scale plume unsteadiness is modelled, not resolved.",
"",
"## Suggested next steps",
"• Optional: extend swirl & steep to full equilibrium (multi-hour) for their final hot steady state.",
"• Mesh-independence on the baseline; an under-sized-airflow case to map the coverage/ACH trade-off.",
])
pdf.close()
print("PDF ->",f"{DEL}/hall_diffuser_setpoint_report.pdf")
