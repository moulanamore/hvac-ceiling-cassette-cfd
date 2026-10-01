import os, sys, numpy as np, vtk
from vtk.util.numpy_support import vtk_to_numpy
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, matplotlib.tri as mtri
CASE=os.path.expanduser("~/mnt/HVAC_claude/room_hvac_case")
tmin=float(sys.argv[1]); tmax=float(sys.argv[2])
for d in ("frames/T","frames/U"): os.makedirs(CASE+"/"+d,exist_ok=True)
r=vtk.vtkOpenFOAMReader(); r.SetFileName(CASE+"/room_hvac_case.foam")
r.CreateCellToPointOn(); r.EnableAllCellArrays(); r.UpdateInformation(); r.Update()
tv=r.GetTimeValues(); times=sorted(t for t in (tv.GetValue(i) for i in range(tv.GetNumberOfValues())) if 0<=t<=60)
def internal(mb):
    best=None
    for i in range(mb.GetNumberOfBlocks()):
        b=mb.GetBlock(i)
        if b is None: continue
        if b.IsA("vtkMultiBlockDataSet"):
            x=internal(b);  best=x if x and (not best or x.GetNumberOfCells()>best.GetNumberOfCells()) else best
        elif b.IsA("vtkUnstructuredGrid"):
            best=b if (not best or b.GetNumberOfCells()>best.GetNumberOfCells()) else best
    return best
plane=vtk.vtkPlane(); plane.SetOrigin(2.75,2.25,1.8); plane.SetNormal(0,1,0)
def frame(t,field,cmap,lo,hi,label,unit):
    ug=internal(r.GetOutput())
    cut=vtk.vtkCutter(); cut.SetCutFunction(plane); cut.SetInputData(ug); cut.Update()
    tf=vtk.vtkTriangleFilter(); tf.SetInputData(cut.GetOutput()); tf.Update(); poly=tf.GetOutput()
    if poly.GetNumberOfPoints()<3: return
    P=vtk_to_numpy(poly.GetPoints().GetData()); x=P[:,0]; z=P[:,2]
    conn=vtk_to_numpy(poly.GetPolys().GetConnectivityArray()).reshape(-1,3)
    a=vtk_to_numpy(poly.GetPointData().GetArray(field)); val=np.linalg.norm(a,axis=1) if a.ndim>1 else a
    tri=mtri.Triangulation(x,z,conn)
    fig,ax=plt.subplots(figsize=(8.2,5.6),dpi=115)
    c=ax.tricontourf(tri,np.clip(val,lo,hi),levels=np.linspace(lo,hi,26),cmap=cmap,extend='both')
    ax.set_aspect('equal'); ax.set_xlim(0,5.5); ax.set_ylim(0,3.7)
    ax.set_xlabel("x (m)"); ax.set_ylabel("z (m)")
    ax.set_title("Ceiling-cassette room  |  %s  |  t = %2d s"%(label,int(t)),fontsize=11)
    cb=fig.colorbar(c,ax=ax,shrink=0.85,pad=0.02); cb.set_label(unit)
    fig.tight_layout(); fig.savefig("%s/frames/%s/%03d.png"%(CASE,field,int(t)),bbox_inches='tight'); plt.close(fig)
n=0
for t in times:
    if t<tmin or t>tmax: continue
    r.UpdateTimeStep(float(t))
    frame(t,"T","coolwarm",289,298,"Temperature","T [K]")
    frame(t,"U","turbo",0.0,0.6,"Velocity magnitude","|U| [m/s]")
    n+=1
print("rendered %d frames for t in [%g,%g]"%(n,tmin,tmax))
