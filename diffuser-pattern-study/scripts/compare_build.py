import os,sys,glob,json,numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
R=sys.argv[1]; OUT=sys.argv[2]
cases={"A":("Baseline 4-way","#2563eb"),"B":("Swirl","#dc2626"),"C":("Steep","#d97706")}
def series(c,n):
    r=[]
    for f in sorted(glob.glob(f"{R}/case{c}_set/postProcessing/{n}/*/*.dat")):
        for ln in open(f):
            if ln.strip() and not ln.startswith('#'):
                p=ln.split()
                try: r.append((float(p[0]),float(p[-1])-273.15))
                except: pass
    return np.array(r)
M={c:json.load(open(f"{OUT}/{c}_metrics.json")) for c in cases}

# ---- 1. trajectory chart (the headline) ----
fig,ax=plt.subplots(figsize=(8,4.6))
for c,(lab,col) in cases.items():
    mm=series(c,"meanT"); rr=series(c,"returnT1")
    if len(mm): ax.plot(mm[:,0],mm[:,1],color=col,lw=2.2,label=f"{lab} — occupied/mean")
    if len(rr): ax.plot(rr[:,0],rr[:,1],color=col,lw=1.1,ls=':',alpha=0.8)
ax.axhline(24,color="#16a34a",lw=1,ls="--"); ax.text(5,24.12,"setpoint 24 °C",color="#16a34a",fontsize=8)
ax.axhline(19.5,color="#64748b",lw=1,ls="--"); ax.text(5,19.62,"return target 19.5 °C (energy balance)",color="#64748b",fontsize=8)
ax.set_xlabel("time (s)"); ax.set_ylabel("temperature (°C)")
ax.set_title("Room mean temperature vs time — only the baseline holds setpoint\n(solid = volume mean, dotted = return air)")
ax.legend(loc="upper left",fontsize=8,framealpha=0.9); ax.grid(alpha=0.25); ax.set_ylim(14,29)
fig.tight_layout(); fig.savefig(f"{OUT}/cmp_trajectory_set.png",dpi=140); plt.close(fig)

# ---- 2. metrics bars ----
labels=[cases[c][0] for c in cases]; cols=[cases[c][1] for c in cases]
cov=[M[c]["comfort_cov"] for c in cases]; adpi=[M[c]["ADPI"] for c in cases]
lag=[ (series(c,"meanT")[-1,1]-series(c,"returnT1")[-1,1]) for c in cases]
fig,axs=plt.subplots(1,3,figsize=(11,3.6))
for ax,vals,ttl,unit,ref in [(axs[0],cov,"Comfort coverage\n(occupied zone 23–26 °C, V<0.35)","%",80),
                              (axs[1],adpi,"ADPI\n(uniformity/draft — see caveat)","",80),
                              (axs[2],lag,"Short-circuit lag\n(mean − return)","°C",None)]:
    b=ax.bar(labels,vals,color=cols,width=0.62)
    if ref: ax.axhline(ref,color="#16a34a",ls="--",lw=1)
    for r,v in zip(b,vals): ax.text(r.get_x()+r.get_width()/2,v,f"{v:.0f}{unit}" if unit=='%' else f"{v:.1f}",ha="center",va="bottom",fontsize=9)
    ax.set_title(ttl,fontsize=9.5); ax.tick_params(axis='x',labelsize=8.5); ax.margins(y=0.18)
fig.suptitle("Three-way setpoint comparison (12 kW load, identical airflow)",fontsize=11)
fig.tight_layout(); fig.savefig(f"{OUT}/cmp_bars_set.png",dpi=140); plt.close(fig)

# ---- 3. coverage-map panel ----
fig,axs=plt.subplots(1,3,figsize=(13.5,3.9))
for ax,c in zip(axs,cases):
    img=plt.imread(f"{OUT}/{c}_coverage.png"); ax.imshow(img); ax.axis("off")
    ax.set_title(f"{cases[c][0]}  (cov {M[c]['comfort_cov']:.0f}%)",fontsize=10)
fig.suptitle("Comfort coverage @1.1 m — green = comfortable, red = outside band",fontsize=11)
fig.tight_layout(); fig.savefig(f"{OUT}/cmp_coverage_panel.png",dpi=130); plt.close(fig)

# ---- 4. data summary ----
summ={}
for c in cases:
    mm=series(c,"meanT"); rr=series(c,"returnT1")
    slope=(mm[-1,1]-mm[mm[:,0]>=mm[-1,0]-50][0,1])/50*60 if len(mm)>2 else 0
    summ[c]=dict(name=cases[c][0],t_end=float(mm[-1,0]),mean=float(mm[-1,1]),ret=float(rr[-1,1]),
                 lag=float(mm[-1,1]-rr[-1,1]),mean_slope_Cmin=float(slope),
                 Tbar=M[c]["Tbar"],Tstd=M[c]["Tstd"],ADPI=M[c]["ADPI"],
                 comfort_cov=M[c]["comfort_cov"],DR_gt20=M[c]["DR_gt20pct"],
                 equilibrated=bool(abs(slope)<0.05))
json.dump(summ,open(f"{OUT}/comparison_summary.json","w"),indent=2)
print("built: cmp_trajectory_set.png, cmp_bars_set.png, cmp_coverage_panel.png, comparison_summary.json")
for c in cases: print(f"  {c} {summ[c]['name']:14s} mean={summ[c]['mean']:.2f} ret={summ[c]['ret']:.2f} lag={summ[c]['lag']:.2f} slope={summ[c]['mean_slope_Cmin']:+.3f} equil={summ[c]['equilibrated']} cov={summ[c]['comfort_cov']:.0f}%")
