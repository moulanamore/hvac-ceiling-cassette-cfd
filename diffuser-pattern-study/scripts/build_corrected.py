import os,sys,json,glob,base64,numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
R,OUT,DEL=sys.argv[1],sys.argv[2],sys.argv[3]; os.makedirs(DEL,exist_ok=True)
cp=1004.4; md=2.227
cases={"A":("Baseline 4-way","#2563eb","caseA_set"),"C":("Steep","#d97706","caseC_set"),"B":("Swirl","#dc2626","caseB_set")}
def dat(c,n):
    r=[]
    for f in sorted(glob.glob(f"{R}/{cases[c][2]}/postProcessing/{n}/*/*.dat")):
        for ln in open(f):
            if ln.strip() and not ln.startswith('#'):
                p=ln.split()
                try:r.append((float(p[0]),float(p[-1])-273.15))
                except:pass
    return np.array(r)
def at(c,n,t=350.0):
    a=dat(c,n); i=int(np.argmin(np.abs(a[:,0]-t))); return a[i,1]
M={c:json.load(open(f"{OUT}/{c}_metrics.json")) for c in cases}
# matched t=350 table values
row={}
for c in cases:
    ret=at(c,"returnT1"); mn=at(c,"meanT")
    row[c]=dict(name=cases[c][0],mean=mn,ret=ret,lag=mn-ret,Tstd=M[c]["Tstd"],ADPI=M[c]["ADPI"],
                cov=M[c]["comfort_cov"],cool=md*cp*(ret-14)/1000.0,
                latest_mean=dat(c,"meanT")[-1,1],latest_t=dat(c,"meanT")[-1,0])

# --- regenerate bars at matched t=350 ---
labels=[row[c]["name"] for c in cases]; cols=[cases[c][1] for c in cases]
fig,axs=plt.subplots(1,3,figsize=(11,3.6))
for ax,key,ttl,unit,ref in [("cov","Comfort coverage @350 s\n(23–26 °C, V<0.35)","%",80),
                            ("ADPI","ADPI (uniformity/draft)\n— see caveat","",80),
                            ("lag","Short-circuit lag @350 s\n(mean − return)","°C",None)] and []:
    pass
def bar(ax,vals,ttl,unit,ref):
    b=ax.bar(labels,vals,color=cols,width=0.62)
    if ref: ax.axhline(ref,color="#16a34a",ls="--",lw=1)
    for r,v in zip(b,vals): ax.text(r.get_x()+r.get_width()/2,v,(f"{v:.0f}{unit}" if unit=='%' else f"{v:.1f}"),ha="center",va="bottom",fontsize=9)
    ax.set_title(ttl,fontsize=9.5); ax.tick_params(axis='x',labelsize=8.5); ax.margins(y=0.18)
bar(axs[0],[row[c]["cov"] for c in cases],"Comfort coverage @350 s\n(23–26 °C, V<0.35 m/s)","%",80)
bar(axs[1],[row[c]["ADPI"] for c in cases],"ADPI (uniformity/draft)\n— misleading, see note","",80)
bar(axs[2],[row[c]["cool"] for c in cases],"Cooling removed @350 s\n(of 12 kW load)","",12)
fig.suptitle("Matched-time comparison at t = 350 s (identical airflow, 12 kW load)",fontsize=11)
fig.tight_layout(); fig.savefig(f"{OUT}/cmp_bars_matched.png",dpi=140); plt.close(fig)

# ================= PDF =================
def page_img(pdf,title,fn,caption,frac=0.60):
    fig=plt.figure(figsize=(8.27,11.69)); fig.text(0.08,0.95,title,fontsize=15,weight="bold")
    ax=fig.add_axes([0.06,0.30,0.88,frac]); ax.imshow(plt.imread(fn)); ax.axis("off")
    fig.text(0.08,0.25,caption,fontsize=9.8,color="#1f2937",wrap=True); pdf.savefig(fig); plt.close(fig)
pdf=PdfPages(f"{DEL}/hall_diffuser_setpoint_report.pdf")
# P1
fig=plt.figure(figsize=(8.27,11.69))
fig.text(0.08,0.95,"Ceiling-Cassette Diffuser Study — Setpoint Comparison",fontsize=15.5,weight="bold")
fig.text(0.08,0.927,"12×10×4 m hall · two 4-way cassettes · identical airflow 1.81 m³/s · 14 °C supply · 12 kW load · OpenFOAM buoyantPimpleFoam, k-ω SST",fontsize=8.6,color="#475569")
fig.text(0.08,0.895,"KEY FINDING",fontsize=12,weight="bold",color="#b91c1c")
kf=("All three patterns remove the SAME air mass (2.23 kg/s) and, by energy balance, all reach the SAME exit-air\n"
"equilibrium (19.4 °C, 12 kW removed). What differs is HOW the air is used. The baseline mixes the supply into the\n"
"room, so its exhaust is warm (carrying heat out) and the occupied zone holds the 24 °C setpoint. Swirl and steep\n"
"SHORT-CIRCUIT — cold supply loops back to the central return before doing work — so at a matched 350 s the room\n"
"is 3–4 °C warmer and far less of the floor is comfortable, and they approach a hotter, slower equilibrium.")
fig.text(0.08,0.79,kf,fontsize=10,color="#0f172a")
ax=fig.add_axes([0.07,0.06,0.86,0.60]); ax.imshow(plt.imread(f"{OUT}/cmp_trajectory_set.png")); ax.axis("off")
pdf.savefig(fig); plt.close(fig)
# P2 matched table + bars
fig=plt.figure(figsize=(8.27,11.69)); fig.text(0.08,0.95,"Matched-time comparison at t = 350 s",fontsize=15,weight="bold")
ax=fig.add_axes([0.06,0.60,0.88,0.30]); ax.imshow(plt.imread(f"{OUT}/cmp_bars_matched.png")); ax.axis("off")
rows=[["Pattern","Occ. mean","Exit/return","Cooling out","Tstd","ADPI","Coverage","Lag"]]
for c in cases:
    d=row[c]; rows.append([d["name"],f"{d['mean']:.1f} °C",f"{d['ret']:.1f} °C",f"{d['cool']:.1f} kW",f"{d['Tstd']:.2f}",f"{d['ADPI']:.0f}",f"{d['cov']:.0f}%",f"{d['lag']:.1f} °C"])
axt=fig.add_axes([0.04,0.30,0.92,0.22]); axt.axis("off")
tb=axt.table(cellText=rows,loc="center",cellLoc="center"); tb.auto_set_font_size(False); tb.set_fontsize(8.3); tb.scale(1,1.6)
for j in range(len(rows[0])): tb[0,j].set_facecolor("#1e3a5f"); tb[0,j].set_text_props(color="white",weight="bold")
fig.text(0.08,0.25,"ADPI caveat:",fontsize=10,weight="bold",color="#b45309")
fig.text(0.08,0.225,"ADPI is scored relative to the LOCAL mean, so swirl's uniformly-too-warm, dead-calm zone scores the highest ADPI\n(82) while giving the lowest real comfort coverage (4%). Rank on absolute coverage + cooling removed, not ADPI alone.",fontsize=9.2,color="#0f172a")
fig.text(0.08,0.17,"Equilibrium note:",fontsize=10,weight="bold",color="#16a34a")
fig.text(0.08,0.145,"Energy balance fixes the exit at 14 + 12000/(2.227·1004) = 19.4 °C and cooling at 12 kW for ALL three — they only\ndiffer in how long they take and how hot the room gets on the way. Baseline is there by ~185 s; swirl is still climbing\n(31.5 °C at 806 s) toward a hotter, slower asymptote. These matched-350 numbers are a snapshot of that approach.",fontsize=9.2,color="#0f172a")
pdf.savefig(fig); plt.close(fig)
# P3 exit flow
fig=plt.figure(figsize=(8.27,11.69)); fig.text(0.08,0.95,"Exit (return) flow — the mechanism",fontsize=15,weight="bold")
ax=fig.add_axes([0.08,0.60,0.84,0.30]); ax.imshow(plt.imread(f"{OUT}/exit_return_trajectory.png")); ax.axis("off")
ax2=fig.add_axes([0.03,0.30,0.94,0.26]); ax2.imshow(plt.imread(f"{OUT}/exit_near_return_slice.png")); ax2.axis("off")
fig.text(0.08,0.25,"The exit-air temperature IS the cooling actually delivered: Q_removed = ṁ·cp·(T_exit − 14).",fontsize=9.6,weight="bold")
fig.text(0.08,0.225,"Baseline exhausts warm (19 °C → 11.6 kW removed); swirl/steep exhaust cold (17 °C → ~8 kW) because cold supply\nshort-circuits straight back into the central return (see the blue air curling into the grille in the slices).",fontsize=9.2,color="#0f172a")
pdf.savefig(fig); plt.close(fig)
# P4 coverage + renders
page_img(pdf,"Comfort coverage @1.1 m (green = comfortable)",f"{OUT}/cmp_coverage_panel.png",
         "Baseline fills the plan; steep leaves gaps; swirl is almost entirely out of band at 350 s.",frac=0.26)
fig=plt.figure(figsize=(8.27,11.69)); fig.text(0.08,0.95,"Flow structure — 3D streamlines from the 8 supply slots",fontsize=13.5,weight="bold")
for i,c in enumerate(["A","C","B"]):
    ax=fig.add_axes([0.05,0.64-0.30*i,0.6,0.27]); ax.imshow(plt.imread(f"{OUT}/render_{c}.png")); ax.axis("off")
    fig.text(0.68,0.78-0.30*i,row[c]["name"],fontsize=11,weight="bold")
    fig.text(0.68,0.75-0.30*i,f"mean {row[c]['mean']:.1f} °C\nexit {row[c]['ret']:.1f} °C\ncoverage {row[c]['cov']:.0f}%",fontsize=9.3)
pdf.savefig(fig); plt.close(fig)
# P5 methodology
fig=plt.figure(figsize=(8.27,11.69)); fig.text(0.08,0.95,"Methodology & caveats",fontsize=15,weight="bold"); y=0.89
for ln in [
"MODEL  OpenFOAM v2012 buoyantPimpleFoam (transient, compressible perfect gas), k-ω SST, 576,000 cells, 4-core.",
"       Hall 480 m³; two 0.6×0.6 m 4-way cassettes (0.4×0.4 central return + 4 supply slots) at (3,5) and (9,5).",
"",
"CONTROLLED VARIABLE  All patterns fix the vertical supply component at −2.83 m/s → identical inlet area 0.64 m²,",
"       identical airflow 1.81 m³/s (13.6 ACH), identical mass flow 2.23 kg/s. Only the horizontal throw differs:",
"       baseline radial, swirl tangential (coherent CCW), steep reduced-throw. Mass conserved to ~1e-10.",
"",
"LOAD / BC  Supply 14 °C; adiabatic walls; 12 kW sensible load (~100 W/m²); uniform-24 °C start.",
"       Energy balance validated: baseline exit 19.2 °C vs 19.4 °C predicted by Q = ṁ·cp·ΔT.",
"",
"WHY THE MEAN DIFFERS (open system)  The room exchanges heat with its surroundings through the return outflow.",
"       dU/dt = Q − ṁ·cp·(T_exit − T_supply). Q, ṁ, T_supply are identical, so the ONLY difference is the exit",
"       temperature, which the flow pattern sets. Lower exit T (short-circuit) → less heat carried out → warmer room.",
"",
"CAVEATS  Comparison is a matched snapshot at t = 350 s. Baseline is at steady state; swirl & steep are still",
"       approaching a hotter equilibrium (very long time-constant due to short-circuiting; not force-converged here).",
"       Single mesh (576k) — mesh-independence pending. RANS (modelled, not resolved, turbulence).",
"",
"NEXT  Mesh-independence on the baseline; an under-sized-airflow case (coverage vs ACH); optional full-asymptote",
"       runs for swirl/steep if the converged hot-equilibrium numbers are needed."]:
    fig.text(0.08,y,ln,fontsize=9.3,color="#0f172a",family="DejaVu Sans"); y-=0.027
pdf.savefig(fig); plt.close(fig); pdf.close()
print("PDF rebuilt:",f"{DEL}/hall_diffuser_setpoint_report.pdf")
json.dump({c:row[c] for c in cases},open(f"{OUT}/matched350_summary.json","w"),indent=2)
