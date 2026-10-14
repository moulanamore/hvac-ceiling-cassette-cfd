import sys, os, json, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
import pyvista as pv
pv.OFF_SCREEN = True

case, label, outdir = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(outdir, exist_ok=True)
os.chdir(case); open("case.foam","a").close()
r = pv.POpenFOAMReader("case.foam")
ts = sorted(float(d) for d in os.listdir('.') if d.replace('.','',1).isdigit() and float(d)>0)
r.set_active_time_value(ts[-1])
mesh = r.read()["internalMesh"]
pd = mesh.cell_data_to_point_data()
names = list(pd.point_data.keys())
Tn = "TMean" if "TMean" in names else "T"
Un = "UMean" if "UMean" in names else "U"
kn = "kMean" if "kMean" in names else ("k" if "k" in names else None)
print(f"[{label}] t={ts[-1]:.0f}  using fields: {Tn},{Un},{kn}  available={names}")

# ---- occupied-zone sample grid (0.3 m wall offset, 0.1-1.8 m height) ----
xs=np.linspace(0.3,11.7,58); ys=np.linspace(0.3,9.7,48); zs=np.linspace(0.1,1.8,12)
XX,YY,ZZ=np.meshgrid(xs,ys,zs,indexing='ij')
pts=np.c_[XX.ravel(),YY.ravel(),ZZ.ravel()]
s=pv.PolyData(pts).sample(pd)
mask = s["vtkValidPointMask"].astype(bool) if "vtkValidPointMask" in s.point_data else np.ones(len(pts),bool)
T=(np.asarray(s[Tn])-273.15)[mask]
U=np.linalg.norm(np.asarray(s[Un]),axis=1)[mask]
Z=ZZ.ravel()[mask]
Tbar=float(T.mean())
EDT=(T-Tbar)-8.0*(U-0.15)
comfort=(EDT>=-1.7)&(EDT<=1.1)&(U<0.35)
ADPI=100.0*comfort.mean()
# draft rating DR (ISO 7730), Tu from TKE if available else 40%
if kn:
    kk=np.clip(np.asarray(s[kn])[mask],0,None)
    Tu=np.clip(np.where(U>1e-3,np.sqrt(2.0/3.0*kk)/np.clip(U,1e-3,None)*100.0,100.0),1,100)
else:
    Tu=np.full_like(U,40.0)
Uc=np.clip(U,0.05,None)
DR=np.clip((34.0-T)*np.power(Uc-0.05,0.62)*(0.37*U*Tu+3.14),0,100)
# vertical stratification: ankle(<=0.3) vs head(>=1.5)
ank=T[Z<=0.3].mean() if (Z<=0.3).any() else np.nan
hed=T[Z>=1.5].mean() if (Z>=1.5).any() else np.nan
M=dict(label=label,time=ts[-1],field=Tn,n=int(mask.sum()),
       Tbar=Tbar,Tstd=float(T.std()),Tmin=float(T.min()),Tmax=float(T.max()),
       ADPI=float(ADPI),DR_mean=float(DR.mean()),DR_gt20pct=float(100*(DR>20).mean()),
       Umean=float(U.mean()),Umax=float(U.max()),
       comfort_cov=float(100*((T>=23)&(T<=26)&(U<0.35)).mean()),
       strat_head_ankle=float(hed-ank) if np.isfinite(hed) and np.isfinite(ank) else None)
json.dump(M,open(f"{outdir}/{label}_metrics.json","w"),indent=2)

# ---- coverage map at 1.1 m: comfort pass/fail (the 'reaches the corners' view) ----
nx,ny=120,100
g=pv.ImageData(dimensions=(nx,ny,1),spacing=(12/nx,10/ny,1),origin=(0,0,1.1)).sample(pd)
Tp=(np.asarray(g[Tn])-273.15).reshape(ny,nx)
Up=np.linalg.norm(np.asarray(g[Un]),axis=1).reshape(ny,nx)
EDTp=(Tp-Tbar)-8.0*(Up-0.15)
cov=((EDTp>=-1.7)&(EDTp<=1.1)&(Up<0.35)).astype(float)
fig,ax=plt.subplots(figsize=(6,5))
im=ax.imshow(cov,origin='lower',extent=[0,12,0,10],cmap='RdYlGn',vmin=0,vmax=1,aspect='equal')
for cx,cy in [(3,5),(9,5)]: ax.plot(cx,cy,'k+',ms=12,mew=2)
ax.set_title(f"{label}: comfort coverage @1.1 m (ADPI={ADPI:.0f})")
ax.set_xlabel('x (m)'); ax.set_ylabel('y (m)')
fig.colorbar(im,ax=ax,shrink=0.85,ticks=[0,1]).set_label('0 = outside comfort   1 = comfortable')
fig.tight_layout(); fig.savefig(f"{outdir}/{label}_coverage.png",dpi=130); plt.close(fig)
print(f"[{label}] ADPI={ADPI:.1f}  Tbar={Tbar:.2f}C  Tstd={T.std():.2f}  DR>20%={100*(DR>20).mean():.1f}%  cov={M['comfort_cov']:.1f}%  strat={M['strat_head_ankle']}")
