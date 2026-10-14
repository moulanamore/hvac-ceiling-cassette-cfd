import sys, os, numpy as np
import pyvista as pv
pv.OFF_SCREEN=True
case=sys.argv[1]; label=sys.argv[2]; out=sys.argv[3]
os.chdir(case); open("case.foam","a").close()
r=pv.POpenFOAMReader("case.foam")
ts=sorted(int(d) for d in os.listdir('.') if d.isdigit() and int(d)>0)
r.set_active_time_value(float(ts[-1]))
m=r.read()["internalMesh"].cell_data_to_point_data()

# seed clusters directly in each of the 8 jets, just below the ceiling
seeds=[]
for cx,cy in [(3,5),(9,5)]:
    for dx,dy in [(0.30,0),(-0.30,0),(0,0.30),(0,-0.30)]:   # E W N S slot centres
        for _ in range(18):
            jx=cx+dx+np.random.uniform(-0.06,0.06)
            jy=cy+dy+np.random.uniform(-0.06,0.06)
            seeds.append([jx,jy,3.80+np.random.uniform(-0.05,0.05)])
seed=pv.PolyData(np.array(seeds))
strm=m.streamlines_from_source(seed, vectors="U", integration_direction="forward",
                               max_length=150.0, initial_step_length=0.2, terminal_speed=1e-5)

p=pv.Plotter(off_screen=True, window_size=[1100,850]); p.set_background("white")
box=pv.Box(bounds=(0,12,0,10,0,4))
p.add_mesh(box, style="wireframe", color="#7a8a96", line_width=1.5)
p.add_mesh(pv.Plane(center=(6,5,0.01),direction=(0,0,1),i_size=12,j_size=10),color="#eef2f5",opacity=0.6)
for cx,cy in [(3,5),(9,5)]:
    p.add_mesh(pv.Cube(center=(cx,cy,3.95),x_length=0.6,y_length=0.6,z_length=0.1),color="#2c3e50")
if strm.n_points>0:
    strm["speed"]=np.linalg.norm(strm["U"],axis=1)
    p.add_mesh(strm.tube(radius=0.035), scalars="speed", cmap="turbo", clim=[0,1.5],
        scalar_bar_args={"title":"|U|  m/s","vertical":True,"position_x":0.9,"position_y":0.25,"height":0.5,"width":0.035,"title_font_size":16,"label_font_size":13})
p.add_text(f"Case {label}", position="upper_left", font_size=18, color="#1a2730")
p.camera_position=[(21,-13,13),(6,5,1.4),(0,0,1)]; p.camera.zoom(1.3)
p.screenshot(f"{out}/render_{label}.png")
print(f"{label}: saved, {strm.n_points} pts, {strm.n_cells} segs")
