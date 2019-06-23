# input: BMP file
# output: gcode

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import imageio
from tqdm import tqdm
import argparse
from gcoder import *

# args  ========================================================================
parser = argparse.ArgumentParser()
parser.add_argument('-f', '--filename', default="files/face_shallow.bmp", help='filename of the bmp file')
parser.add_argument('-w', '--width', default=150, help='width of the grid')
parser.add_argument('-t', '--height', default=150, help='height of the grid')
parser.add_argument('-l', '--n_layers', default=4, help='layer numbers to print at each pixel')
parser.add_argument('-g', '--gap', default=1.0, help='gap between two parallel paths')
parser.add_argument('-v', '--visualize', default=False, help='option to visualize the shrinkage')
args = parser.parse_args()
GAP = args.gap
grid_shape = [args.width, args.height]
dir_bmp = args.filename
n_layers = args.n_layers
visualize = args.visualize

# init  ========================================================================
bmp = imageio.imread(dir_bmp)
bmp = bmp[:, :, 0] if len(bmp.shape) == 3 else bmp   # remove extra channels
bmp = bmp / 255     # normalized bmp: each unit is shrinkage: 0~1

grid = np.zeros(grid_shape)
points = []

# map bmp to grid
for r, row in enumerate(grid):
    for c, col in enumerate(row):
        h = int(r / grid.shape[0] * bmp.shape[0])
        w = int(c / grid.shape[1] * bmp.shape[1])
        grid[r][c] = bmp[h][w]

# horizontal paths, grid -> points
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
            s = grid[i_row][i_col]  # normalized shrinkage 0 ~ 1
            e = 1.0
            # points.append((x, y, s, e))
            points.append(param_to_point(x, y, s, e))

# vertical paths, grid -> points
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
            # points.append((x, y, s, e))
            points.append(param_to_point(x, y, s, e))


# points_on_grid to points_print
# for i, point in enumerate(points):
#     x, y, s, e = point
#     x += (200 - grid.shape[0]) / 2
#     y += (220 - grid.shape[1]) / 2
#     x *= GAP
#     y *= GAP
#     d = 0.05 * s + 0.2 * (1 - s)
#     points[i] = {
#         'x': x,
#         'y': y,
#         'layer_thickness': d,
#         'E_ratio': e
#     }
points = translate(points, [(200 - grid.shape[0]) / 2, (220 - grid.shape[1]) / 2])
points = scale(points, GAP)


# compile from points to gcode
gcode = points_to_gcode(points)

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

