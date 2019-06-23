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
file_name = '0121_platform_flat_test'

with open('files/'+file_name+'.yaml', 'r') as stream:
    params = yaml.load(stream)

gcodes = ""
for args in params:
    m = Mesh(args['m'], args['n'], args['gap'])
    points_list = m.print()
    points_dict = points_list_to_dict(points_list)

    points = translate(points_dict, [args['x'], args['y']])
    gcode = points_to_gcode(points,
                        Z_OFFSET=args['z_offset'],
                        n_layers=args['n_layers'],
                       layer_thickness_default=args['layer_thickness_default'],
                        E_ratio_default=args['E_ratio_default'],
                        F_default=args['F_default'],
                       fan_default=args['fan_default'])
    gcodes += gcode

ofile = open('tmp/output.gcode', 'w')
ofile.write(gcodes)
ofile.close()











# visualization
if args['visualize']:
    # replace with Line_Collection
    xs = []
    ys = []

    points = [(p['x'], p['y'], p['layer_thickness'], p['E_ratio']) for p in points]

    points = np.array(points)

    # visualization
    colors = points[:, 2]
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

