import sys, os, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pyvista as pv
pv.OFF_SCREEN=True
case=sys.argv[1]; label=sys.argv[2]; outdir=sys.argv[3]
os.makedirs(outdir, exist_ok=True); os.chdir(case); open("case.foam","a").close()
r=pv.POpenFOAMReader("case.foam")
times=sorted(float(d) for d in os.listdir('.') if d.replace('.','',1).isdigit() and float(d)>0)
r.set_active_time_value(times[-1])
m=r.read()["internalMesh"]
nm=list(m.cell_data.keys())+list(m.point_data.keys())
Tn="TMean" if "TMean" in nm else "T"; Un="UMean" if "UMean" in nm else "U"
def samp_plane(origin):
    g=pv.ImageData(dimensions=(120,100,1),spacing=(12/120,10/100,1),origin=origin); return g.sample(m)
s=samp_plane((0,0,1.1))
T=(np.asarray(s[Tn])-273.15).reshape(100,120); U=np.linalg.norm(np.asarray(s[Un]),axis=1).reshape(100,120)
def heat(a,ttl,fn,cmap,vmin,vmax,cbl):
    fig,ax=plt.subplots(figsize=(6,5)); im=ax.imshow(a,origin='lower',extent=[0,12,0,10],cmap=cmap,vmin=vmin,vmax=vmax,aspect='equal')
    for cx,cy in [(3,5),(9,5)]: ax.plot(cx,cy,'k+',ms=12,mew=2)
    ax.set_xlabel('x (m)'); ax.set_ylabel('y (m)'); ax.set_title(f"{label}: {ttl}")
    cb=fig.colorbar(im,ax=ax,shrink=0.85); cb.set_label(cbl); fig.tight_layout(); fig.savefig(fn,dpi=130); plt.close(fig)
heat(T,"Mean temperature @1.1 m",f"{outdir}/{label}_T_plane.png","coolwarm",21,27,"T (°C)")
heat(U,"Mean air speed @1.1 m",f"{outdir}/{label}_U_plane.png","viridis",0,0.6,"|U| (m/s)")
xs=np.linspace(0,12,120); zs=np.linspace(0,4,80); XX,ZZ=np.meshgrid(xs,zs)
pts=np.c_[XX.ravel(),np.full(XX.size,5.0),ZZ.ravel()]; pc=pv.PolyData(pts).sample(m)
Tv=(np.asarray(pc[Tn])-273.15).reshape(80,120); Uv=np.linalg.norm(np.asarray(pc[Un]),axis=1).reshape(80,120)
def vs(a,ttl,fn,cmap,vmin,vmax,cbl):
    fig,ax=plt.subplots(figsize=(7,3)); im=ax.imshow(a,origin='lower',extent=[0,12,0,4],cmap=cmap,vmin=vmin,vmax=vmax,aspect='equal')
    for cx in [3,9]: ax.plot(cx,3.98,'kv',ms=8)
    ax.set_xlabel('x (m)'); ax.set_ylabel('z (m)'); ax.set_title(f"{label}: {ttl} (y=5 slice)")
    cb=fig.colorbar(im,ax=ax,shrink=0.9); cb.set_label(cbl); fig.tight_layout(); fig.savefig(fn,dpi=130); plt.close(fig)
vs(Tv,"Mean temperature",f"{outdir}/{label}_T_slice.png","coolwarm",14,27,"T (°C)")
vs(Uv,"Mean air speed",f"{outdir}/{label}_U_slice.png","viridis",0,2.0,"|U| (m/s)")
print(f"{label}: 4 figs ({Tn}/{Un}) -> {outdir}")
