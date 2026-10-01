import os
SRC  = os.path.expanduser("~/mnt/HVAC_claude/room_cfd_geometry")
CASE = os.path.expanduser("~/mnt/HVAC_claude/room_hvac_case")
TRI  = os.path.join(CASE, "constant/triSurface")
SYS  = os.path.join(CASE, "system")
for d in (TRI, SYS): os.makedirs(d, exist_ok=True)

# patch name, source stl, snappy type, refinement level
PATCHES = [
  ("floor","floor.stl","wall",1),
  ("roof","roof.stl","wall",1),
  ("walls","walls.stl","wall",1),
  ("window","window.stl","wall",1),
  ("person_1","person_1.stl","wall",2),
  ("person_2","person_2.stl","wall",2),
  ("person_3","person_3.stl","wall",2),
  ("equipment","equipment.stl","wall",2),
  ("ac_cassette","ac_cassette.stl","wall",2),
  ("supply","ac_supply_inlet.stl","patch",2),
  ("outlet","ac_return_outlet.stl","patch",2),
]

def process_stl(src, dst, name, scale=0.001):
    bb=[[1e18]*3,[-1e18]*3]; out=[]
    with open(src) as f:
        for line in f:
            s=line.strip()
            if s.startswith("solid"):      out.append("solid %s\n"%name)
            elif s.startswith("endsolid"): out.append("endsolid %s\n"%name)
            elif s.startswith("vertex"):
                p=s.split(); x,y,z=float(p[1])*scale,float(p[2])*scale,float(p[3])*scale
                for i,v in enumerate((x,y,z)): bb[0][i]=min(bb[0][i],v); bb[1][i]=max(bb[1][i],v)
                out.append("    vertex %.6e %.6e %.6e\n"%(x,y,z))
            else: out.append(line if line.endswith("\n") else line+"\n")
    open(dst,"w").writelines(out); return bb

g=[[1e18]*3,[-1e18]*3]
for name,fn,typ,lvl in PATCHES:
    bb=process_stl(os.path.join(SRC,fn), os.path.join(TRI,name+".stl"), name)
    for i in range(3): g[0][i]=min(g[0][i],bb[0][i]); g[1][i]=max(g[1][i],bb[1][i])

base=0.15
mn=[round(g[0][i]-0.10,3) for i in range(3)]
mx=[round(g[1][i]+0.10,3) for i in range(3)]
nx=max(1,int(round((mx[0]-mn[0])/base)))
ny=max(1,int(round((mx[1]-mn[1])/base)))
nz=max(1,int(round((mx[2]-mn[2])/base)))
loc=(2.0,1.0,0.5)

def header(obj,cls="dictionary"):
    return ("/*--------------------------------*- C++ -*----------------------------------*/\n"
            "FoamFile\n{\n    version     2.0;\n    format      ascii;\n    class       %s;\n    object      %s;\n}\n"
            "// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //\n\n"%(cls,obj))

# ---- blockMeshDict ----
v=[(mn[0],mn[1],mn[2]),(mx[0],mn[1],mn[2]),(mx[0],mx[1],mn[2]),(mn[0],mx[1],mn[2]),
   (mn[0],mn[1],mx[2]),(mx[0],mn[1],mx[2]),(mx[0],mx[1],mx[2]),(mn[0],mx[1],mx[2])]
bm=header("blockMeshDict")+"convertToMeters 1;\n\nvertices\n(\n"
for p in v: bm+="    (%.4f %.4f %.4f)\n"%p
bm+=");\n\nblocks\n(\n    hex (0 1 2 3 4 5 6 7) (%d %d %d) simpleGrading (1 1 1)\n);\n\nedges ();\n\n"%(nx,ny,nz)
bm+=("boundary\n(\n    outer\n    {\n        type patch;\n        faces\n        (\n"
     "            (0 3 2 1)\n            (4 5 6 7)\n            (0 1 5 4)\n            (2 3 7 6)\n            (1 2 6 5)\n            (0 4 7 3)\n        );\n    }\n);\n\nmergePatchPairs ();\n")
open(os.path.join(SYS,"blockMeshDict"),"w").write(bm)

# ---- surfaceFeatureExtractDict ----
sf=header("surfaceFeatureExtractDict")
for name,fn,typ,lvl in PATCHES:
    sf+=("%s.stl\n{\n    extractionMethod    extractFromSurface;\n"
         "    extractFromSurfaceCoeffs { includedAngle 150; }\n    writeObj yes;\n}\n\n"%name)
open(os.path.join(SYS,"surfaceFeatureExtractDict"),"w").write(sf)

# ---- snappyHexMeshDict ----
sh=header("snappyHexMeshDict")
sh+="castellatedMesh true;\nsnap            true;\naddLayers       true;\n\ngeometry\n{\n"
for name,fn,typ,lvl in PATCHES:
    sh+="    %s.stl { type triSurfaceMesh; name %s; }\n"%(name,name)
sh+="}\n\ncastellatedMeshControls\n{\n    maxLocalCells 2000000;\n    maxGlobalCells 6000000;\n    minRefinementCells 10;\n    nCellsBetweenLevels 3;\n    maxLoadUnbalance 0.10;\n    resolveFeatureAngle 30;\n    allowFreeStandingZoneFaces true;\n\n    features\n    (\n"
for name,fn,typ,lvl in PATCHES:
    sh+='        { file "%s.eMesh"; level %d; }\n'%(name,lvl)
sh+="    );\n\n    refinementSurfaces\n    {\n"
for name,fn,typ,lvl in PATCHES:
    sh+="        %s { level (%d %d); patchInfo { type %s; } }\n"%(name,lvl,lvl,typ)
sh+="    }\n\n    refinementRegions {}\n\n    locationInMesh (%.3f %.3f %.3f);\n}\n\n"%loc
sh+=("snapControls\n{\n    nSmoothPatch 3;\n    tolerance 2.0;\n    nSolveIter 50;\n    nRelaxIter 5;\n"
     "    nFeatureSnapIter 10;\n    implicitFeatureSnap false;\n    explicitFeatureSnap true;\n    multiRegionFeatureSnap false;\n}\n\n")
sh+="addLayersControls\n{\n    relativeSizes true;\n    expansionRatio 1.2;\n    finalLayerThickness 0.4;\n    minThickness 0.1;\n    layers\n    {\n"
for name,fn,typ,lvl in PATCHES:
    if typ=="wall": sh+="        %s { nSurfaceLayers 2; }\n"%name
sh+=("    }\n    nGrow 0;\n    featureAngle 130;\n    slipFeatureAngle 30;\n    nRelaxIter 5;\n    nSmoothSurfaceNormals 1;\n"
     "    nSmoothNormals 3;\n    nSmoothThickness 10;\n    maxFaceThicknessRatio 0.5;\n    maxThicknessToMedialRatio 0.3;\n"
     "    minMedialAxisAngle 90;\n    nBufferCellsNoExtrude 0;\n    nLayerIter 50;\n}\n\n")
sh+=("meshQualityControls\n{\n    maxNonOrtho 65;\n    maxBoundarySkewness 20;\n    maxInternalSkewness 4;\n    maxConcave 80;\n"
     "    minVol 1e-13;\n    minTetQuality 1e-15;\n    minArea -1;\n    minTwist 0.02;\n    minDeterminant 0.001;\n    minFaceWeight 0.05;\n"
     "    minVolRatio 0.01;\n    minTriangleTwist -1;\n    nSmoothScale 4;\n    errorReduction 0.75;\n}\n\n")
sh+="mergeTolerance 1e-6;\n"
open(os.path.join(SYS,"snappyHexMeshDict"),"w").write(sh)

# ---- minimal supporting dicts ----
cd=header("controlDict")+("application     buoyantSimpleFoam;\nstartFrom       startTime;\nstartTime       0;\n"
    "stopAt          endTime;\nendTime         1;\ndeltaT          1;\nwriteControl    timeStep;\nwriteInterval   100;\n"
    "purgeWrite      0;\nwriteFormat     ascii;\nwritePrecision  7;\nwriteCompression off;\ntimeFormat      general;\n"
    "timePrecision   6;\nrunTimeModifiable true;\n")
open(os.path.join(SYS,"controlDict"),"w").write(cd)
fs=header("fvSchemes")+("ddtSchemes { default steadyState; }\ngradSchemes { default Gauss linear; }\n"
    "divSchemes { default none; }\nlaplacianSchemes { default Gauss linear corrected; }\n"
    "interpolationSchemes { default linear; }\nsnGradSchemes { default corrected; }\n")
open(os.path.join(SYS,"fvSchemes"),"w").write(fs)
fv=header("fvSolution")+("solvers {}\nSIMPLE { nNonOrthogonalCorrectors 0; }\n")
open(os.path.join(SYS,"fvSolution"),"w").write(fv)

# ---- Allmesh runner ----
al=("#!/bin/sh\ncd \"${0%/*}\" || exit 1\n"
    "echo '==> 1/4 surfaceFeatureExtract'; surfaceFeatureExtract\n"
    "echo '==> 2/4 blockMesh';            blockMesh\n"
    "echo '==> 3/4 snappyHexMesh';        snappyHexMesh -overwrite\n"
    "echo '==> 4/4 checkMesh';            checkMesh -allGeometry -allTopology\n"
    "echo 'DONE. Inspect with:  paraFoam   (or  touch case.foam )'\n")
open(os.path.join(CASE,"Allmesh"),"w").write(al); os.chmod(os.path.join(CASE,"Allmesh"),0o755)

print("Case written ->", CASE)
print("Domain (m): min", mn, "max", mx, "| blockMesh cells:", nx,"x",ny,"x",nz,"=",nx*ny*nz)
print("locationInMesh:", loc)
print("Patches:", ", ".join(p[0] for p in PATCHES))
