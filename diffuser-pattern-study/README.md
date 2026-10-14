# Diffuser-Pattern Setpoint Study — Dual Ceiling-Cassette Hall

**Does the air-conditioning actually reach every corner — and is it a capacity problem or a distribution problem?**
A transient OpenFOAM study that holds cooling capacity fixed and varies only the supply-diffuser airflow pattern, to find out.

> 12 m × 10 m × 4 m hall (480 m³) · two four-way ceiling cassettes · identical airflow **1.81 m³/s (13.6 ACH)** · identical **12 kW** load · `buoyantPimpleFoam`, k-ω SST, 576k cells.

---

## TL;DR — pattern, not capacity, decides coverage

At **identical** air mass flow (2.23 kg/s) and **identical** 12 kW load, only the baseline four-way throw conditions the occupied zone. The swirl and steep variants **short-circuit** — cold supply loops straight back into the central return — so they deliver only part of the cooling and the room runs 3–4 °C warmer.

| Pattern | Occupied mean | Exit (return) T | Cooling delivered | Comfort coverage |
|---|---|---|---|---|
| **A — Baseline** (radial 45°) | **24.4 °C** | 19.2 °C | **11.6 kW** | **89 %** |
| **C — Steep** (reduced throw) | 27.1 °C | 17.7 °C | 8.2 kW | 68 % |
| **B — Swirl** (tangential) | 27.9 °C | 16.8 °C | 6.2 kW | 4 % |

*Matched snapshot at t = 350 s from a common 24 °C start.*

![Room temperature vs time](thesis/figs/cmp_trajectory_set.png)

*The baseline flattens at setpoint; swirl and steep keep climbing toward hotter, slower equilibria.*

---

## 1. The setup

A rectangular hall served by two four-way cassettes at (3, 5) m and (9, 5) m. Each cassette has a central return grille surrounded by four directional supply slots.

![Hall layout](thesis/figs/fig_geometry_plan.png)

The three patterns differ **only** in the horizontal direction of the supply jets; every slot keeps the same downward component (−2.83 m/s), so the inlet area (0.64 m²) and the airflow are identical — the pattern is the only variable.

![The three patterns](thesis/figs/fig_patterns.png)

| Input | Value |
|---|---|
| Solver / turbulence | `buoyantPimpleFoam` (transient, compressible) / k-ω SST |
| Airflow / supply T | 1.81 m³/s (13.6 ACH) / 14 °C |
| Mass flow | 2.23 kg/s (identical across A, B, C) |
| Load | 12 kW sensible (~100 W/m²), adiabatic walls |
| Mesh | 576,000 hex cells, 4-core parallel |
| Start | uniform 24 °C, still air |

---

## 2. The mechanism — it's all in the exit air

The exit (return) temperature **is** the cooling delivered: `Q = ṁ·cp·(T_exit − 14)`. The baseline exhausts *warm* air (it mixed with the room and carried heat out → 11.6 kW). Swirl and steep exhaust *cold* air (supply short-circuits to the grille → only 6–8 kW).

![Exit flow near the cassettes](thesis/figs/exit_near_return_slice.png)

*Near-ceiling slice: in swirl/steep the cold (blue) supply curls straight back into the central return; in the baseline the returning air is warmer, having mixed with the room first.*

> **Why can the mean differ if everything is conserved?** The hall is an *open* system. From `dU/dt = Q − ṁ·cp·(T_exit − T_supply)`, the source, mass flow and supply temperature are identical across cases — the only term that differs is the exit temperature, which the pattern sets. A short-circuiting pattern carries less heat out, so its room runs warmer. Conservation makes the books balance; it does not make the balance the same number. (All three do reach the same 19.4 °C exit equilibrium eventually — they differ in how fast, and how hot the room gets meanwhile.)

---

## 3. Comfort coverage

![Comfort coverage maps](thesis/figs/cmp_coverage_panel.png)

*Green = comfortable (23–26 °C, V < 0.35 m/s), red = outside. Baseline fills the plan; steep leaves gaps; swirl is almost entirely out of band.*

![Matched-time metrics](thesis/figs/cmp_bars_matched.png)

> **ADPI alone is a trap.** The swirl case scores the *highest* ADPI (82) yet has the *lowest* comfort coverage (4 %). ADPI is measured relative to the local mean, so a uniformly-too-warm, dead-calm zone scores well. Rank on absolute comfort coverage and cooling delivered, not ADPI.

---

## 4. Flow structure

| Baseline | Swirl | Steep |
|---|---|---|
| ![A](thesis/figs/render_A.png) | ![B](thesis/figs/render_B.png) | ![C](thesis/figs/render_C.png) |

*Streamlines from the eight supply slots — note the longer near-ceiling recirculation feeding the return in the swirl case.*

---

## 5. Conclusions

- **Capacity was identical; distribution was not.** The baseline holds 24 °C with 89 % coverage; swirl and steep leave the occupied zone 3–4 °C warmer (4 % and 68 % coverage).
- **Short-circuiting is the mechanism**; the exit temperature and the mean-minus-exit "short-circuit lag" (5 / 9 / 11 °C for baseline / steep / swirl) diagnose it cleanly.
- For this geometry the conventional **baseline four-way throw is clearly best**; a swirl pattern is counter-productive when the return sits in the middle of the same cassette.
- **ADPI must not be used alone** — it rewarded the worst pattern.

*Limitations: matched-time snapshot (swirl/steep still approaching hotter equilibria); single mesh; RANS turbulence. Next steps: mesh-independence and a reduced-airflow case.*

---

## Full write-up & contents

📄 **Full thesis:** [`thesis/hall_diffuser_thesis.pdf`](thesis/hall_diffuser_thesis.pdf) · [`.docx`](thesis/hall_diffuser_thesis.docx)
📊 **Report & interactive dashboard:** [`deliverables/`](deliverables/)

```
thesis/        full write-up (docx + pdf + source + figures)
deliverables/  standalone report PDF + interactive HTML dashboard
scripts/       PyVista / matplotlib post-processing + parallel run scripts
cases/         reproducible OpenFOAM setup (mesh dicts + 3 case configs)
```

Reproduce: the three cases differ only in `0.orig/U` (supply direction); build the mesh from `cases/mesh/` (blockMesh → topoSet → createPatch), then per case `decomposePar` → `mpirun -np 4 buoyantPimpleFoam -parallel` → `reconstructPar`.
