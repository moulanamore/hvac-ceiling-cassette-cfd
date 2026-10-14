# Diffuser-Pattern Setpoint Study — Dual Ceiling-Cassette Hall

Transient CFD comparison of three supply-diffuser airflow patterns in a
12 m × 10 m × 4 m (480 m³) hall served by two four-way ceiling cassettes,
under **identical cooling airflow** (1.81 m³/s, ≈13.6 ACH) and an
**identical 12 kW sensible load**. The only variable is the horizontal
direction of the supply jets.

**Solver:** OpenFOAM v2012 `buoyantPimpleFoam` (transient, compressible),
k–ω SST, 576k-cell structured mesh, 4-core parallel.

## Key finding

At identical airflow and load, the supply **pattern** — not capacity —
decides whether the air reaches the occupied zone:

| Pattern | Occ. mean | Exit (return) T | Cooling removed | Comfort coverage |
|---|---|---|---|---|
| A — Baseline (radial 45°) | 24.4 °C | 19.2 °C | 11.6 kW | 89 % |
| C — Steep (reduced throw) | 27.1 °C | 17.7 °C | 8.2 kW | 68 % |
| B — Swirl (tangential)    | 27.9 °C | 16.8 °C | 6.2 kW | 4 % |

*(matched snapshot at t = 350 s; identical 2.23 kg/s air mass flow)*

The baseline mixes supply into the room and exhausts warm air (carrying
heat out); swirl and steep **short-circuit** cold supply straight back
into the central return, delivering only part of the cooling and leaving
the occupied zone 3–4 °C warmer. By energy balance all three reach the
same exit equilibrium (19.4 °C, 12 kW removed) — they differ in how the
air is used and how hot the occupied zone gets. ADPI alone is shown to be
misleading (it rewards the uniformly-too-warm swirl case).

## Layout

- `thesis/` — full write-up (`hall_diffuser_thesis.docx`, `.pdf`, source `thesis.md`) and all figures (`figs/`)
- `deliverables/` — standalone report PDF and interactive self-study dashboard (HTML)
- `scripts/` — post-processing & figure/report generators (PyVista, matplotlib, pythermalcomfort) and the parallel run scripts
- `cases/` — reproducible OpenFOAM setup: shared mesh dicts (`cases/mesh/`) and the three case configs (`system/`, `constant/`, `0.orig/`); mesh and solution data are not committed (regenerate with blockMesh + topoSet + createPatch)

## Reproduce (outline)

```
# build the mesh (from cases/mesh dicts, in a case dir)
blockMesh && topoSet && createPatch -overwrite
# per case: initialise, decompose, run in parallel, reconstruct
cp -r 0.orig 0 && decomposePar -force
mpirun -np 4 buoyantPimpleFoam -parallel && reconstructPar -latestTime
```

The three cases differ only in the supply velocity vectors in `0.orig/U`
(baseline radial, swirl tangential, steep reduced-throw); the vertical
component (−2.83 m/s) and inlet area (0.64 m²) are identical, so the air
mass flow is the controlled variable.
