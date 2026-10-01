# geometry/ — how the geometry was created (historical)

These scripts document how the room geometry was first generated. They are kept
for provenance and are **not** the regeneration path for the committed case.

- `build_room.py` — FreeCAD (Part workbench) macro. Parametric room: 5.5 × 4.5 m
  plan, mono-pitch roof 3.6 → 2.8 m, three occupant boxes, an equipment box, a
  window on the Y=0 wall, and (in this original version) a protruding ceiling
  cassette. Exports STLs. Run from the FreeCAD Python console:
  `exec(open("build_room.py").read())`. Output dir is `$HVAC_BASE/room_cfd_geometry`
  (defaults to the current working directory).
- `make_case.py` — **superseded.** Original assembly of an all-STL
  `snappyHexMesh` case. It does not reproduce the committed case.

## What the committed case actually uses

The committed case was reworked after these scripts:

- The **room shell** (floor, walls, sloped roof) is a body-fitted `blockMesh`
  block whose inclined top face is the mono-pitch roof — not STL-meshed.
- Only the **occupant and equipment** obstacles are STL-meshed by `snappyHexMesh`
  (`constant/triSurface/person_1..3.stl`, `equipment.stl`).
- The **supply ring, central outlet and window** patches are carved from clean
  boundary faces with `topoSet` + `createPatch`. This replaced carving the
  diffuser from the protruding cassette's baffle faces, which had a
  near-cancelling net face area and throttled the ventilation flux to ~0
  (see the report, §5).

To (re)build the mesh for the committed case, run `./Allmesh` from the repo root.
