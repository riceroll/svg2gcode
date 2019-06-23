# input: BMP file
# output: gcode

import numpy as np
import yaml
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import imageio
from tqdm import tqdm
import argparse
from gcoder import *

# args  ========================================================================
parser = argparse.ArgumentParser()
parser.add_argument('-f', '--filename', default="0122_cone", help='filename of the yaml file')
parser.add_argument('-m', '--map', default="0", help='filename of the npy file')
parser.add_argument('-v', '--visualize', default="1", help='visualization')
args = parser.parse_args()

with open('files/' + args.filename + '.yaml', 'r') as stream:
    params = yaml.load(stream)

gcodes = ""
for param in params:
    m = Mesh(param['m'], param['n'], param['gap'])
    if int(args.map):
        m.shrink(args.filename)
    points_list = m.print()
    points_dict = points_list_to_dict(points_list)

    points = translate(points_dict, [param['x'], param['y']])
    gcode = points_to_gcode(points,
                            Z_OFFSET=param['z_offset'],
                            n_layers=param['n_layers'],
                            layer_thickness_default=param['layer_thickness_default'],
                            E_ratio_default=param['E_ratio_default'],
                            F_default=param['F_default'],
                            fan_default=param['fan_default'])
    gcodes += gcode

ofile = open('tmp/'+args.filename+'.gcode', 'w')
ofile.write(gcodes)
ofile.close()











# visualization
if args.visualize:
    # replace with Line_Collection
    xs = []
    ys = []

    points = [(p['x'], p['y'], p['layer_thickness'], p['E_percentage']) for p in points]

    points = np.array(points)

    # visualization
    colors = points[:, 3]
    paths = points[:, :2]
    paths = paths.reshape(-1, 1, 2)

    segments = np.hstack([paths[:-1], paths[1:]])
    coll = LineCollection(segments, cmap=plt.cm.gist_ncar)
    coll.set_array(colors)

    fig, ax = plt.subplots()
    ax.add_collection(coll)
    ax.autoscale_view()

    plt.axis('equal')
    plt.show()

