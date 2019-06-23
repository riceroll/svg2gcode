import sys

import numpy as np

sys.path.append("/Users/Roll/Riceroll/repository/code/")
from gcoder import *

import matplotlib
import matplotlib.cm as cm

from open3d import *


# %% args

path = '/Users/Roll/desktop/test/'

trim_s = [4, -4]
trim_p = [0, -1]
ifile_2d_name = 'nefertiti100.st'
v_gap = 0.05
translation = [-30, -30]
ifile_2d_name = 'two_hills_print.st'
ifile_2d_name = 'face_flatten_print.st'
v_gap = 0.025
translation = [0, 0]
ifile_2d_name = 'two30_print.st'
v_gap = 1
translation = [0, 0]
ifile_2d_name = 'nefereti_print.st'
v_gap = 0.025
translation = [0, 0]
trim_s = [100, -1]
trim_p = [0, -1500]
ifile_2d_name = 'face_dense.st'
v_gap = 0.038
translation = [0, 0]
trim_s = [200, -200]
trim_p = [0, -1]
ifile_2d_name = 'dome.st.print'
v_gap = 1.8
translation = [0, 0]
trim_s = [0, -1]
trim_p = [0, -1]
# ifile_2d_name = 'two60.st.print'
# v_gap = 1
# translation = [0, 0]
# trim_s = [0, -1]
# trim_p = [0, -1]
ifile_2d_name = 'hat.st.print'
v_gap = 1
translation = [0, 0]
trim_s = [1000, -1000]
trim_p = [0, -1]



gap_size_2d = 0.35
visualization = True
gcode_gen = True
gap_size = 0.6

shrinkage_min = 0.07
shrinkage_max = 0.33

print_gap = 0.4

# %% main

ofile_name = ifile_2d_name
ifile = open(path + ifile_2d_name)
ofile = open(path + ofile_name+".gcode", 'w')

content = ifile.read()
lines = content.split('\n')

scale_3d = 1.0

# import points
points = []
for line in lines:
    point = []
    items = line.split()
    if len(items) > 6:
        for item in items[-5:]:
            point.append(float(item))
        point[0] *= scale_3d
        point[1] *= scale_3d
        point[2] *= scale_3d
        points.append(point)

# compute shrinkage
points_new = []
for i, point in enumerate(points):
    if i == 0:
        E_percentage = 0
        layer_thickness = 0.2
        s = 0.2
    else:
        point_prev = points[i-1]
        dist_3d = dist3d(point[0], point[1], point[2],point_prev[0], point_prev[1], point_prev[2])
        dist_2d = dist3d(point[3], point[4], 0, point_prev[3], point_prev[4], 0)
        if dist_2d != 0:
            s = (dist_2d - dist_3d) / dist_2d
        else:
            s = 0.5
        E_percentage = 1

    point_new = {
        "x": point[-2],
        "y": point[-1],
        "E_percentage": E_percentage,
        "shrinkage": s
    }
    if layer_thickness < 0:
        print(layer_thickness)
    points_new.append(point_new)

points_new = points_new[trim_p[0]: trim_p[1]]

# smooth
# for j in range(400):
#     for i, p in enumerate(points_new):
#         if i != 0:
#             p['shrinkage'] = (points_new[i-1]['shrinkage'] + p['shrinkage']) / 2

shrinkages = [p["shrinkage"] for p in points_new]
max_s = max(sorted(shrinkages)[trim_s[0]:trim_s[1]])
min_s = min(sorted(shrinkages)[trim_s[0]:trim_s[1]])
for i, p in enumerate(points_new):
    s = (p['shrinkage'] - min_s) / (max_s - min_s) * (0.33 - 0.07) + 0.07
    # s = p['shrinkage']

    points_new[i]['shrinkage'] = s
    layer_thickness = shrinkage_to_layerthickness(s)
    points_new[i]['layer_thickness'] = layer_thickness

shrinkages = [p["shrinkage"] for p in points_new]
layer_thicknesses = [p['layer_thickness'] for p in points_new]
min_l = min(sorted(layer_thicknesses)[5:-5])
max_l = max(sorted(layer_thicknesses)[5:-5])


scale(points_new, print_gap / v_gap)
translate(points_new, translation)

gcode = points_to_gcode(points_new)
ofile.write(gcode)
ofile.close()


#%% visualization

norm = matplotlib.colors.Normalize(vmin=min_l, vmax=max_l, clip=True)
mapper = cm.ScalarMappable(norm=norm, cmap=cm.hsv)

ps = []
ls = []
ss = []
cs = []

for i, point in enumerate(points_new):
    p = [point['x'], point['y'], 0]
    ps.append(p)
    if i != 0:
        l = [i-1, i]
        ls.append(l)
    s = point['shrinkage']
    ss.append(s)

colors = list(mapper.to_rgba(np.array(layer_thicknesses[1:])))
for i, c in enumerate(colors):
    cs.append([c[0], c[1], c[2]])

line_set = LineSet()
line_set.points = Vector3dVector(ps)
line_set.lines = Vector2iVector(ls)
line_set.colors = Vector3dVector(cs)
draw_geometries([line_set])
