import os,sys,glob,numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
import pyvista as pv
pv.OFF_SCREEN=True
R=sys.argv[1]; OUT=sys.argv[2]
cases={"A":("Baseline","#2563eb",f"{R}/caseA_set",500),"C":("Steep","#d97706",f"{R}/caseC_set",350),"B":("Swirl","#dc2626",f"{R}/caseB_set",350)}
# ---- (1) return (exit) temperature trajectory ----
def ser(c,n):
    r=[]
    for f in sorted(glob.glob(f"{cases[c][2]}/postProcessing/{n}/*/*.dat")):
        for ln in open(f):
            if ln.strip() and not ln.startswith('#'):
                p=ln.split()
                try: r.append((float(p[0]),float(p[-1])-273.15))
                except: pass
    return np.array(r)
fig,ax=plt.subplots(figsize=(8,4.4))
for c,(lab,col,_,_) in cases.items():
    rr=ser(c,"returnT1")
    if len(rr): ax.plot(rr[:,0],rr[:,1],color=col,lw=2.2,label=f"{lab} — return (exit) air")
ax.axhline(14,color="#0ea5e9",ls="--",lw=1); ax.text(5,14.15,"supply in = 14 °C",color="#0ea5e9",fontsize=8)
ax.axhline(19.4,color="#16a34a",ls="--",lw=1); ax.text(5,19.55,"equilibrium exit = 19.4 °C (all cases, energy balance)",color="#16a34a",fontsize=8)
ax.set_xlabel("time (s)"); ax.set_ylabel("return / exit air temperature (°C)")
ax.set_title("Exit (return) air temperature — the cooling actually removed\nlower exit T = more short-circuit = less heat carried out")
ax.legend(loc="lower right",fontsize=9); ax.grid(alpha=0.25); ax.set_ylim(13.5,20.5)
fig.tight_layout(); fig.savefig(f"{OUT}/exit_return_trajectory.png",dpi=140); plt.close(fig)

# ---- (2) near-cassette vertical slice: T + in-plane streamlines, showing air drawn into the return ----
fig,axs=plt.subplots(1,3,figsize=(14,4.2))
for ax,c in zip(axs,["A","C","B"]):
    lab,col,path,tv=cases[c]
    os.chdir(path); open("case.foam","a").close()
    r=pv.POpenFOAMReader("case.foam"); r.set_active_time_value(float(tv)); m=r.read()["internalMesh"]
    nx,nz=240,80; xs=np.linspace(0,12,nx); zs=np.linspace(0,4,nz); XX,ZZ=np.meshgrid(xs,zs)
    pts=np.c_[XX.ravel(),np.full(XX.size,5.0),ZZ.ravel()]; s=pv.PolyData(pts).sample(m)
    T=(np.asarray(s["T"])-273.15).reshape(nz,nx); U=np.asarray(s["U"]); Ux=U[:,0].reshape(nz,nx); Uz=U[:,2].reshape(nz,nx)
    im=ax.imshow(T,origin='lower',extent=[0,12,0,4],cmap="coolwarm",vmin=14,vmax=30,aspect='equal')
    ax.streamplot(xs,zs,Ux,Uz,density=1.3,color='k',linewidth=0.5,arrowsize=0.7)
    for cx in [3,9]:
        ax.add_patch(plt.Rectangle((cx-0.3,3.9),0.6,0.1,color='k'))            # cassette
        ax.annotate("return",(cx,3.9),(cx,3.3),ha='center',fontsize=7,color='white',
                    arrowprops=dict(arrowstyle='->',color='white'))
    ax.set_xlim(0,12); ax.set_ylim(2.3,4); ax.set_title(f"{lab}  (exit T = {ser(c,'returnT1')[-1,1]:.1f} °C)",fontsize=10)
    ax.set_xlabel("x (m)"); ax.set_ylabel("z (m)")
cb=fig.colorbar(im,ax=axs,shrink=0.8,pad=0.01); cb.set_label("T (°C)")
fig.suptitle("Near-ceiling flow into the return — cold air short-circuiting straight back to the grille (B,C) vs mixed warm return (A)",fontsize=10.5)
fig.savefig(f"{OUT}/exit_near_return_slice.png",dpi=135,bbox_inches='tight'); plt.close(fig)
print("wrote exit_return_trajectory.png, exit_near_return_slice.png")
for c in cases: print(f"  {c} {cases[c][0]:9s} exit T = {ser(c,'returnT1')[-1,1]:.2f} C  (cooling removed = 2.227*1004*(T-14) = {2.227*1004.4*(ser(c,'returnT1')[-1,1]-14)/1000:.1f} kW of 12)")
