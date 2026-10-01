ROOM HVAC CFD  ->  snappyHexMesh case  (all lengths in metres; STLs scaled from mm)

DOMAIN:  0..5.5 x 0..4.5 m, mono-pitch roof 3.6 -> 2.8 m,  volume ~79 m3
BACKGROUND BLOCK:  [-0.1,-0.1,-0.1] .. [5.6,4.6,3.7],  38x31x25 = 29,450 cells (base 0.15 m)
locationInMesh:  (2.0 1.0 0.5)

PATCHES (constant/triSurface) + suggested BCs for the solution step:
  floor        wall    adiabatic or fixed T                       refine L1
  roof         wall    external roof/solar load or adiabatic      L1
  walls        wall    adiabatic                                  L1
  window       wall*   OUTDOOR / atmospheric: fixed To (e.g. 42C) or
                       externalWallHeatFluxTemperature + solar q  L1
  person_1..3  wall    ~75 W each  (q ~ 26 W/m2)  or T ~ 31 C     L2
  equipment    wall    ~200 W      (q ~ 70 W/m2)                  L2
  ac_cassette  wall    adiabatic diffuser body                    L2
  supply       inlet   cold supply ~16 C, ~0.8 m/s (~10 ACH, A=0.26 m2)  L2
  outlet       outlet  pressureOutlet 0 gauge (A=0.16 m2)         L2
  * window is a WALL in the mesh; set its thermal/outdoor BC in 0/T at the
    solution step. If instead you want it as an air OPENING (infiltration /
    natural vent), change its type to 'patch' in snappyHexMeshDict.

RUN:
  cd room_hvac_case
  ./Allmesh              # surfaceFeatureExtract -> blockMesh -> snappyHexMesh -overwrite -> checkMesh
  # inspect:  touch case.foam   (open in ParaView)  or  paraFoam

OPENFOAM VERSION NOTES:
  - ESI (openfoam.com, v1706+): rename system/surfaceFeatureExtractDict ->
    surfaceFeaturesDict and call 'surfaceFeatures' instead of 'surfaceFeatureExtract'
    (same dict content works). Everything else is identical.
  - Foundation (openfoam.org, v11/12): use as-is.

TUNING:
  - base cell size: edit 'blocks (...)' in system/blockMeshDict
  - per-patch refinement: 'level (n n)' in snappyHexMeshDict/refinementSurfaces
  - boundary layers: addLayers true (2 layers on walls); set false for a quick
    first mesh if layers struggle on tight corners (window reveal, cassette edges)
