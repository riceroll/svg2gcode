import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import imageio
import copy
from tqdm import tqdm
from gcoder import *


# constants
GAP = 1.0   # gap between two parallel lines

# variables
grid_shape = [50, 50]
dir_bmp = "files/face_shallow.bmp"
n_layers = 4
visualize = False

# init
bmp = imageio.imread(dir_bmp)
bmp = bmp[:, :, 0] if len(bmp.shape) == 3 else bmp   # remove extra channels
bmp = bmp / 255     # normalized bmp: each unit is shrinkage: 0~1

grid = np.zeros(grid_shape)
points = []

# normalized bmp to grid
for r, row in enumerate(grid):
    for c, col in enumerate(row):
        h = int(r / grid.shape[0] * bmp.shape[0])
        w = int(c / grid.shape[1] * bmp.shape[1])
        grid[r][c] = bmp[h][w]

# grid to points_on_grid
for i_row, row in enumerate(grid):
    is_even = True if i_row % 2 == 0 else False
    ran = np.arange(row.shape[0])
    if is_even:
        ran = ran[::-1]
    for i_col in ran:
        i_col_r = i_col-1 if is_even else i_col+1
        if True:
            x = float(i_col)
            y = float(i_row)
            s = grid[i_row][i_col]  # normalized shrinkage 0~1
            e = 1.0
            points.append((x, y, s, e))

for i_col, col in enumerate(grid.T):
    is_even = True if i_col % 2 == 0 else False
    ran = np.arange(col.shape[0])
    if is_even:
        ran = ran[::-1]
    for i_row in ran:
        i_row_r = i_row-1 if is_even else i_row+1
        if True:
            y = float(i_row)
            x = float(i_col)
            s = grid[i_row][i_col]
            e = 1.0
            points.append((x, y, s, e))


points_new = copy.deepcopy(points)
for i, point in enumerate(points):
    x, y, s, e = point

    x += (200 - grid.shape[0]) / 2
    y += (220 - grid.shape[1]) / 2
    x -= grid.shape[0]
    y -= grid.shape[1]

    x *= GAP
    y *= GAP

    d = 0.1

    points_new[i] = {
        'x': x,
        'y': y,
        'layer_thickness': d,
        'E_ratio': e
    }

cmds = points_to_cmds(points_new, 0.07)
gcode1 = cmds_to_gcode(cmds)


points_new = copy.deepcopy(points)
for i, point in enumerate(points):
    x, y, s, e = point

    x += (200 - grid.shape[0]) / 2
    y += (220 - grid.shape[1]) / 2
    x += grid.shape[0]
    y += grid.shape[1]

    x *= GAP
    y *= GAP

    # d = 0.05 * s + 0.2 * (1 - s)
    d = 0.1

    points_new[i] = {
        'x': x,
        'y': y,
        'layer_thickness': d,
        'E_ratio': e
    }

cmds = points_to_cmds(points_new, 0.1)
gcode2 = cmds_to_gcode(cmds)


points_new = copy.deepcopy(points)
for i, point in enumerate(points):
    x, y, s, e = point

    x += (200 - grid.shape[0]) / 2
    y += (220 - grid.shape[1]) / 2
    x += grid.shape[0]
    y -= grid.shape[1]

    x *= GAP
    y *= GAP

    d = 0.1

    points_new[i] = {
        'x': x,
        'y': y,
        'layer_thickness': d,
        'E_ratio': e
    }

cmds = points_to_cmds(points_new, 0.13)
gcode3 = cmds_to_gcode(cmds)


points_new = copy.deepcopy(points)
for i, point in enumerate(points):
    x, y, s, e = point

    x += (200 - grid.shape[0]) / 2
    y += (220 - grid.shape[1]) / 2
    x -= grid.shape[0]
    y += grid.shape[1]

    x *= GAP
    y *= GAP

    d = 0.1

    points_new[i] = {
        'x': x,
        'y': y,
        'layer_thickness': d,
        'E_ratio': e
    }

cmds = points_to_cmds(points_new, 0.16)
gcode4 = cmds_to_gcode(cmds)

gcode = gcode2 + gcode4 + gcode1 + gcode3


ofile = open('tmp/output.gcode','w')
ofile.write(gcode)
ofile.close()


# visualization
if visualize:
    # replace with Line_Collection
    xs = []
    ys = []

    points = [(p['x'], p['y'], p['layer_thickness'], p['E_ratio']) for p in points]

    points = np.array(points)

    # visualization
    colors = points[:, 2]
    paths = points[:, :2]
    paths = paths.reshape(-1, 1, 2)
    # points = points[:20]

    segments = np.hstack([paths[:-1], paths[1:]])
    coll = LineCollection(segments, cmap=plt.cm.gist_ncar)
    coll.set_array(colors)

    fig, ax = plt.subplots()
    ax.add_collection(coll)
    ax.autoscale_view()

    plt.axis('equal')
    plt.show()

