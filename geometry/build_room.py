# -*- coding: utf-8 -*-
# ================================================================
#  Single-floor sloping-roof room -> HVAC CFD geometry (v2)
#  + ceiling cassette AC, + window wall patch, larger volume.
#  FreeCAD Part workbench, parametric. Units: mm
#  Run (FreeCAD Python console): exec(open("build_room.py").read())
# ================================================================
# =====================================================================
#  HISTORICAL geometry generator (v2): builds the room shell, occupants,
#  equipment, window and a PROTRUDING ceiling cassette as STLs. The committed
#  case uses only the occupant/equipment obstacle STLs; the room shell and
#  the ceiling diffuser are generated instead by blockMesh + topoSet
#  (see ./Allmesh). Kept to document how the geometry was first created.
# =====================================================================
import os, math, glob
import FreeCAD as App
import Part
from FreeCAD import Vector
try:
    import FreeCADGui as Gui
except Exception:
    Gui = None

# ------------------------- PARAMETERS ---------------------------
W      = 5500.0     # room width  (X)
D      = 4500.0     # room depth  (Y)
H_HIGH = 3600.0     # eave height at high side (X=0)
H_LOW  = 2800.0     # eave height at low  side (X=W)  -> mono-pitch roof

PEOPLE = [          # standing occupant boxes: x0,y0,sx,sy,sz
    (1300.0, 1100.0, 400.0, 350.0, 1700.0),
    (2900.0, 2900.0, 400.0, 350.0, 1700.0),
    (3900.0, 1300.0, 400.0, 350.0, 1700.0),
]
EQUIP = (4500.0, 3400.0, 600.0, 600.0, 900.0)   # heat box: x0,y0,sx,sy,sz

CASS   = 840.0      # ceiling cassette square face size
CASS_D = 300.0      # cassette protrusion below ceiling
RET_H, IN_H, SUP_H = 200.0, 280.0, 380.0   # concentric half-sizes (OUT = CASS/2 = 420)

WIN_W, WIN_H, WIN_SILL = 2400.0, 1500.0, 900.0   # window on Y=0 wall

BASE = os.environ.get("HVAC_BASE", os.getcwd())  # set HVAC_BASE to control output location
OUT  = os.path.join(BASE, "room_cfd_geometry")
# ----------------------------------------------------------------

def roof_z(x):
    return H_HIGH + (H_LOW - H_HIGH) * (x / W)

for n in list(App.listDocuments().keys()):
    if n == "Room_HVAC_CFD":
        App.closeDocument(n)
doc = App.newDocument("Room_HVAC_CFD")

# room air volume (trapezoid in XZ extruded in Y)
prof = Part.makePolygon([Vector(0,0,0), Vector(W,0,0), Vector(W,0,H_LOW), Vector(0,0,H_HIGH), Vector(0,0,0)])
room_shape = Part.Face(prof).extrude(Vector(0, D, 0))
room = doc.addObject("Part::Feature","Room_AirVolume"); room.Shape = room_shape

people = []
for i,(x0,y0,sx,sy,sz) in enumerate(PEOPLE,1):
    o = doc.addObject("Part::Feature","Person_%d"%i)
    o.Shape = Part.makeBox(sx,sy,sz, Vector(x0,y0,0)); people.append(o)

ex,ey,esx,esy,esz = EQUIP
equip = doc.addObject("Part::Feature","Equipment_Heat")
equip.Shape = Part.makeBox(esx,esy,esz, Vector(ex,ey,0))

# ceiling cassette
ccx, ccy = W/2.0, D/2.0
half = CASS/2.0
top_z = roof_z(ccx+half) - 10.0
bz    = top_z - CASS_D
cass_shape = Part.makeBox(CASS, CASS, CASS_D, Vector(ccx-half, ccy-half, bz))
ac = doc.addObject("Part::Feature","AC_Cassette"); ac.Shape = cass_shape

def sqw(hs, z):
    return Part.makePolygon([Vector(ccx-hs,ccy-hs,z), Vector(ccx+hs,ccy-hs,z),
                             Vector(ccx+hs,ccy+hs,z), Vector(ccx-hs,ccy+hs,z), Vector(ccx-hs,ccy-hs,z)])
return_face = Part.Face(sqw(RET_H, bz))
inner_band  = Part.Face([sqw(IN_H, bz),  sqw(RET_H, bz)])
supply_face = Part.Face([sqw(SUP_H, bz), sqw(IN_H, bz)])
outer_frame = Part.Face([sqw(half,  bz), sqw(SUP_H, bz)])
supply = doc.addObject("Part::Feature","AC_Supply_Inlet"); supply.Shape = supply_face
outlet = doc.addObject("Part::Feature","AC_Return_Outlet"); outlet.Shape = return_face

# window patch on Y=0 wall
wx0, wx1 = W/2.0 - WIN_W/2, W/2.0 + WIN_W/2
wz0, wz1 = WIN_SILL, WIN_SILL + WIN_H
win_face = Part.Face(Part.makePolygon([Vector(wx0,0,wz0), Vector(wx1,0,wz0), Vector(wx1,0,wz1), Vector(wx0,0,wz1), Vector(wx0,0,wz0)]))
window = doc.addObject("Part::Feature","Window"); window.Shape = win_face

# fluid domain
obst = [o.Shape for o in people] + [equip.Shape, cass_shape]
union = obst[0]
for s in obst[1:]: union = union.fuse(s)
fluid_shape = room_shape.cut(union)
fluid = doc.addObject("Part::Feature","Fluid_Domain"); fluid.Shape = fluid_shape
doc.recompute()

# classify room boundary faces, cut window from Y=0 wall
floor_f, roof_f, wall_items = [], [], []
for f in room_shape.Faces:
    n = f.normalAt(0,0); c = f.CenterOfMass
    if abs(n.z) < 0.3:   wall_items.append((f,n,c))
    elif c.z < 1.0:      floor_f.append(f)
    else:                roof_f.append(f)
walls_final = []
for f,n,c in wall_items:
    if abs(n.y) > 0.9 and c.y < 1.0:
        f = f.cut(win_face)
    walls_final.append(f)

# export STL patches (clean stale files first)
if not os.path.isdir(OUT): os.makedirs(OUT)
for p in glob.glob(os.path.join(OUT,"*.stl")) + glob.glob(os.path.join(OUT,"*.step")):
    try: os.remove(p)
    except Exception: pass
def stl(shape,name): shape.exportStl(os.path.join(OUT, name+".stl"))
Part.makeCompound(floor_f).exportStl(os.path.join(OUT,"floor.stl"))
Part.makeCompound(roof_f).exportStl(os.path.join(OUT,"roof.stl"))
Part.makeCompound(walls_final).exportStl(os.path.join(OUT,"walls.stl"))
stl(win_face, "window")
for i,o in enumerate(people,1): stl(o.Shape,"person_%d"%i)
stl(equip.Shape, "equipment")
Part.makeCompound([fc for fc in cass_shape.Faces if fc.CenterOfMass.z > bz+1.0] + [inner_band, outer_frame]).exportStl(os.path.join(OUT,"ac_cassette.stl"))
stl(supply_face, "ac_supply_inlet")
stl(return_face, "ac_return_outlet")
stl(fluid_shape, "fluid_domain")

Part.export([room, equip, ac, supply, outlet, window] + people, os.path.join(OUT,"room_hvac_parts.step"))
Part.export([fluid], os.path.join(OUT,"fluid_domain.step"))
doc.saveAs(os.path.join(OUT,"Room_HVAC_CFD.FCStd"))

if Gui is not None and App.GuiUp:
    def col(o,rgb,t=0): o.ViewObject.ShapeColor=rgb; o.ViewObject.Transparency=int(t)
    col(room,(0.60,0.80,1.00),82)
    for o in people: col(o,(0.95,0.60,0.20))
    col(equip,(0.85,0.25,0.20)); col(ac,(0.80,0.80,0.88))
    col(supply,(0.10,0.45,0.95)); col(outlet,(0.95,0.35,0.10)); col(window,(0.45,0.75,0.95),55)
    fluid.ViewObject.Visibility=False
    Gui.activeDocument().activeView().viewAxonometric()
    Gui.SendMsgToActiveView("ViewFit")

slope = math.degrees(math.atan((H_HIGH-H_LOW)/W))
vol = W*(H_HIGH+H_LOW)/2.0*D/1e9
print("==== Room_HVAC_CFD v2 ====")
print("Room %.0f x %.0f mm | roof %.0f->%.0f (%.2f deg) | volume ~ %.1f m3" % (W,D,H_HIGH,H_LOW,slope,vol))
print("Ceiling cassette (supply ring + central return) + window on Y=0 wall")
print("Outputs ->", OUT)
