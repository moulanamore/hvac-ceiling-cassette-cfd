# ParaView batch: render temperature & velocity animations of the Y=2.25 slice
# Run:  & "C:\Program Files\ParaView 5.11.0\bin\pvbatch.exe" anim.py
from paraview.simple import *
import os
CASE = "C:/Users/moula/HVAC_claude/room_hvac_case"

foam = OpenFOAMReader(FileName=CASE + "/room_hvac_case.foam")
foam.MeshRegions = ['internalMesh']
UpdatePipeline()

scene = GetAnimationScene()
scene.UpdateAnimationUsingDataTimeSteps()
nT = len(foam.TimestepValues)

view = GetActiveViewOrCreate('RenderView')
view.ViewSize = [1280, 720]
view.OrientationAxesVisibility = 0
view.CameraParallelProjection = 1
view.Background = [1, 1, 1]

sl = Slice(Input=foam)
sl.SliceType = 'Plane'
sl.SliceType.Origin = [2.75, 2.25, 1.8]
sl.SliceType.Normal = [0, 1, 0]
disp = Show(sl, view)

# face-on view of the X-Z slice (looking +Y), Z up
view.CameraPosition   = [2.75, -20, 1.6]
view.CameraFocalPoint = [2.75, 2.25, 1.6]
view.CameraViewUp     = [0, 0, 1]
view.CameraParallelScale = 2.4
Render()

def run(field, comp, lo, hi, folder, preset):
    outdir = CASE + "/frames/" + folder
    try: os.makedirs(outdir)
    except OSError: pass
    if comp: ColorBy(disp, ('POINTS', field, comp))
    else:    ColorBy(disp, ('POINTS', field))
    tf = GetColorTransferFunction(field)
    tf.ApplyPreset(preset, True)
    tf.RescaleTransferFunction(lo, hi)
    disp.SetScalarBarVisibility(view, True)
    Render()
    SaveAnimation(outdir + "/" + field + ".png", view,
                  ImageResolution=[1280, 720], FrameWindow=[0, nT-1])
    print("wrote", nT, "frames ->", outdir)

run('T', None,       289.0, 298.0, 'T_slice', 'Cool to Warm')   # 16-25 C
run('U', 'Magnitude', 0.0,   0.6,  'U_slice', 'Turbo')          # 0-0.6 m/s

print("DONE. Frames in", CASE + "/frames")
