import sys

import numpy as np
from gcoder import *

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from mpl_toolkits.mplot3d.art3d import Line3DCollection
import matplotlib.cm as cm


# %% args

path = '/Users/Roll/desktop/Geodesy_II/'
# ifile_2d_name = 'hill_2D_Vidya_optimized'
ifile_2d_name = 'hill_2D_optimized_6'
version = '0'
ifile_3d_name = 'hill_3D'
#
# ifile_2d_name = 'two_hills_man_0'
# ifile_3d_name = 'two_hills_man'
#
# ifile_2d_name = 'onion2D_0'
# ifile_3d_name = 'onion3D'

ifile_2d_name = sys.argv[1]


gap_size_2d = 0.35
visualization = True
gcode_gen = True

shrinkage_min = 0.07
shrinkage_max = 0.33

# %% loading

ofile_name = ifile_2d_name
ifile_2d = open(path + ifile_2d_name + '.obj')
ifile_3d = open(path + ifile_3d_name + '.obj')
ofile = open(path + ofile_name + '_' + str(version) + '.gcode', 'w')


#%% funcions

def file_to_lines(ifile):
    content = ifile.read()
    lines = content.split('\n')
    return lines


def get_points_2d_path(lines):
    points = []
    path_prev = -1
    for line in lines:
        items = line.split()
        if len(items) == 0:
            continue

        if items[1] == "gap_size":  # get gap_size
            gap_size = float(items[2])

        if items[0] == 'v':  # 2D vertices
            x = float(items[1])
            y = float(items[2])
            point = {'x': x, 'y': y}
            points.append(point)

        if items[0] == 'l':  # path springs
            points[0]['shrinkage'] = 0
            shrinkage = float(items[4])
            layer_thickness = shrinkage_to_layerthickness(shrinkage)
            points[int(items[2])]['shrinkage'] = shrinkage
    return points, gap_size


def get_points_2d_gap(lines, points_2d):
    points_gap = []
    for line in lines:
        items = line.split()
        if len(items) == 0:
            continue

        if items[0] == 's':     # gap springs
            i0 = int(items[1])
            i1 = int(items[2])
            seg = [[points_2d[i0]['x'], points_2d[i0]['y']], [points_2d[i1]['x'], points_2d[i1]['y']]]
            points_gap.append(seg)

    return points_gap


def smooth_shrinkage(points_2d, n_iter=3):
    for iter in range(n_iter):
        half_window_size = n_iter - iter

        for i, p in enumerate(points_2d[half_window_size:-half_window_size]):
            i += half_window_size

            shrinkages_window = [pp['shrinkage'] for pp in (points_2d[i - half_window_size:i + 1 + half_window_size])]
            neighbor_window = shrinkages_window[:half_window_size] + shrinkages_window[-half_window_size:]
            avg_shrinkages_neighbor = np.mean(np.array(neighbor_window))
            sd_shrinkages_neighbor = np.sqrt(np.var(neighbor_window))
            sd_center = abs(p['shrinkage'] - avg_shrinkages_neighbor)

            if sd_center > sd_shrinkages_neighbor:
                shrinkage = (shrinkages_window[half_window_size - 1] + shrinkages_window[half_window_size + 1]) / 2
                points_2d[i]['shrinkage'] = shrinkage
    return points_2d


def compile_shrinkage(points_2d, l=True, f=False):
    for i, p in enumerate(points_2d):
        layer_thickness = shrinkage_to_layerthickness(p['shrinkage'])
        F = int(p['shrinkage'] * 10000)
        points_2d[i]['F'] = F
        points_2d[i]['layer_thickness'] = layer_thickness


def save_gcode(points_2d, ofile=ofile):
    gcode = points_to_gcode(points_2d)
    ofile.write(gcode)
    ofile.close()


def visualize(points_2d, points_gap, save_image=True, show_image=True):
    # segs_path
    points_from = np.array([[p['x'], p['y']] for p in points_2d[:-1]])
    points_to = np.array([[p['x'], p['y']] for p in points_2d[1:]])
    segs_path = np.concatenate([points_from, points_to], axis=1)
    segs_path = segs_path.reshape(-1, 2, 2)

    # shrinkage to color
    shrinkages = []
    for p in points_2d[1:]:
        try:
            shrinkages.append(p['shrinkage'])
        except:
            shrinkages.append(0)
    shrinkages = np.array(shrinkages)

    shrinkages = shrinkages * (shrinkages > shrinkage_min) * (shrinkages < shrinkage_max)\
                 + shrinkage_max * (shrinkages >= shrinkage_max) + shrinkage_min * (shrinkages <= shrinkage_min)
    norm = matplotlib.colors.Normalize(vmin=shrinkage_min, vmax=shrinkage_max, clip=True)
    mapper = cm.ScalarMappable(norm=norm, cmap=cm.hsv)
    color = mapper.to_rgba(shrinkages)

    # segs_gap
    segs_gap = np.array(points_gap).reshape(-1, 2, 2)

    # create line collections
    lc_path = LineCollection(segs_path, color=color)
    lc_gap = LineCollection(segs_gap)

    # render
    fig, ax = plt.subplots()
    ax.add_collection(lc_gap)
    ax.add_collection(lc_path)

    ax.grid(False)
    ax.set_xlim(-40, 60)
    ax.set_ylim(-40, 40)
    plt.axis('off')
    plt.axis('equal')

    # save image
    plt.savefig(path + ifile_2d_name + '_' + str(version) + '.png')

    if show_image:
        plt.show()



# %% main

lines_2d = file_to_lines(ifile_2d)

# points_2d_path
points_2d, gap_size_3d = get_points_2d_path(lines_2d)
# points_2d = smooth_shrinkage(points_2d)
points_2d = scale(points_2d, gap_size_2d / gap_size_3d)  # scale for printing
points_2d = translate(points_2d, [0, 20])

# points_2d_gap
points_gap = get_points_2d_gap(lines_2d, points_2d)

if visualization:
    visualize(points_2d, points_gap)

if gcode_gen:
    save_gcode(points_2d)

