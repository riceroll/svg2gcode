import math
import os
import copy
import numpy as np

E_RATIO = 0.063 * 1.0  # unit thickness, unit distance, E_RATIO * distance * layer_thickness = extrusion
# E_RATIO = 0.166     # E = E_RATIO * distance(mm) * layernthickness(mm)

# args
PRINTER = 'MB'
LAYER_THICKNESS_DEFAULT = 0.1
Z_OFFSET_DEFAULT = 0.0
E_RATIO_DEFAULT = 1 * E_RATIO
F_DEFAULT = 3500
N_LAYERS = 6

# const
MB_GCODE_HEAD = open(os.path.abspath(os.path.join(os.path.split(os.path.realpath(__file__))[0], "../data/MB_HEAD.gcode"))).read()
MB_GCODE_TAIL = open(os.path.abspath(os.path.join(os.path.split(os.path.realpath(__file__))[0], "../data/MB_GCODE_TAIL.gcode"))).read()
MB_LAYER_TAIL = open(os.path.abspath(os.path.join(os.path.split(os.path.realpath(__file__))[0], "../data/MB_LAYER_TAIL.gcode"))).read()

TEMPLATE = {}
TEMPLATE["HEAD"] = MB_GCODE_HEAD
TEMPLATE["LAYER"] = MB_LAYER_TAIL
TEMPLATE["TAIL"] = MB_GCODE_TAIL

y = [0.05, 0.07, 0.1, 0.12, 0.15, 0.17, 0.2, 0.22, 0.25, 0.27, 0.3] # layer_thickness
x = [0.3727, 0.3047, 0.24, 0.2067, 0.1533, 0.1467, 0.118, 0.1113, 0.1013, 0.0907, 0.0793]   # shrinkage
z = np.polyfit(x, y, 3)
poly = np.poly1d(z)

def dist(p1, p2):
    dis = math.sqrt((p1['x']-p2['x'])**2+(p1['y']-p2['y'])**2)
    return dis


def dist2(x, y, x_prev, y_prev):
    dis = math.sqrt((x-x_prev)**2 + (y-y_prev)**2)
    return dis


def dist3d(x1, y1, z1, x2, y2, z2):
    dis = math.sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2) + (z1 - z2) * (z1 - z2))
    return dis


def shrinkage_to_layerthickness(shrinkage):
    l = poly(shrinkage)
    if l > 0.3:
        l = 0.3
    if l < 0.05:
        l = 0.05
    return l

def param_to_point(x, y, s, e):
    """
    :param s: percentage it shrinks by
    :param e: extrusion percentage [0.0, 1.0]
    :return: point: {'x', 'y', 'layer_thickness', 'E_ratio'}
    """
    # l = shrinkage_to_layerthickness(s)
    l = -1
    e = (1 - s / 0.2) * 1.5 + 0.5
    f = int((s / 0.2) * 2500 + 1000)
    point = {
        'x': x,
        'y': y,
        'layer_thickness': l,
        'E_percentage': e,
        'F': f
    }
    return point


def points_list_to_dict(points):
    points_new = []
    for point in points:
        point_new = param_to_point(point[0], point[1], point[2], point[3])
        points_new.append(point_new)
    return points_new


def points_to_cmds(points,
                   Z_OFFSET=Z_OFFSET_DEFAULT,
                   n_layers=4,
                   layer_thickness_default=[LAYER_THICKNESS_DEFAULT, LAYER_THICKNESS_DEFAULT, LAYER_THICKNESS_DEFAULT, LAYER_THICKNESS_DEFAULT],
                   E_ratio_default=[E_RATIO_DEFAULT,E_RATIO_DEFAULT,E_RATIO_DEFAULT,E_RATIO_DEFAULT],
                   F_default=[F_DEFAULT, F_DEFAULT, F_DEFAULT, F_DEFAULT],
                   fan_default=[0, 255, 255, 255]
                   ):
    """
    :param points: [point_0, point_1, ...]
                point:  {'x', 'y', 'layer_thickness', 'E_percentage': 0~1}
    :return: cmds: [cmd_0, cmd_1, cmd_2, ...]
                cmd: {'cmd': first term in gcode, ...}
    """

    # compile commands for one layer ==================================================================================
    cmds = []   # cmds for one layer
    E_sum = 0   # sum of extrusion for one layer
    X_prev = Y_prev = 0
    for i, point in enumerate(points):
        X = point['x']
        Y = point['y']
        d = dist2(X, Y, X_prev, Y_prev) if i != 0 else 0
        e_ratio = point['E_percentage'] if 'E_percentage' in point else 1       # percentage of extrusion per distance per layer_thickness
        e_ratio_thickness = e_ratio * d * 1.0     # extrusion for the distance of this command per layer thickness
        l = point['layer_thickness'] if 'layer_thickness' in point else -1      # layer thickness, by default, it is calculated in the global part
        F = point['F'] if 'F' in point else -1
        X_prev = X
        Y_prev = Y
        cmds.append({'X': X, 'Y': Y, 'l': l, 'E': e_ratio_thickness, 'F': F, 'cmd': 'G1'})
    # hard code special commands
    cmds.insert(0, {'cmd': ';', 'layer': -1})   # comment showing the layer

    # compile cmds for one layer to the final commands for the whole print ===========================================
    cmds_global = []
    for i_layer in range(n_layers):
        E_sum = 0
        x_prev = None
        y_prev = None
        for cmd in cmds:
            cmd_new = copy.copy(cmd)
            if cmd_new['cmd'] == 'M106':
                cmd_new['S'] = fan_default[i_layer]
            if cmd_new['cmd'] == 'G1' and cmd_new['l'] is not None:     # it has layer thickness and x and y
                if cmd_new['l'] == -1:
                    cmd_new['l'] = layer_thickness_default[i_layer]
                if not x_prev:
                    x_prev = cmd_new['X']
                    y_prev = cmd_new['Y']
                d = dist2(cmd_new['X'], cmd_new['Y'], x_prev, y_prev)
                E_current = cmd_new['E'] * cmd_new['l'] * E_ratio_default[i_layer]
                # print(cmd_new['E'],cmd_new['l'],E_ratio_default[i_layer],cmd_new['E'] * cmd_new['l'] * E_ratio_default[i_layer])
                E_sum += E_current
                if PRINTER == 'UM':
                    cmd_new['E'] = E_sum
                else:
                    cmd_new['E'] = E_current
                cmd_new['Z'] = cmd_new['l'] * (i_layer + 1) + Z_OFFSET
                # cmd_new['Z'] = sum(layer_thickness_default[:i_layer+1]) + Z_OFFSET
                cmd_new['F'] = cmd_new['F'] if cmd_new['F'] != -1 else F_default[i_layer]
            if cmd_new['cmd'] == ';':
                cmd_new['layer'] = i_layer+1
            cmds_global.append(cmd_new)
    # hard code HEAD and TAIL of the gcode
    cmds_global.insert(0, {'cmd': 'HEAD'})
    cmds_global.append({'cmd': 'TAIL'})


    return cmds_global


def cmds_to_gcode(cmds):
    """
    :param cmds: [cmd_0, cmd_1, cmd_2, ...]
            cmd: {'cmd': first term in gcode, ...}
    :return: gcode: string
    """
    gcode = ""
    for cmd in cmds:
        code = ""
        if cmd['cmd'] == 'HEAD' or cmd['cmd'] == 'TAIL':
            code += TEMPLATE[cmd['cmd']]
        elif cmd['cmd'] == 'G1':
            code += "G1 "
            if cmd['X'] is not None:
                code += "X{0:.3f} Y{1:.3f} Z{2:.3f} ".format(cmd['X'], cmd['Y'], cmd['Z'])
            code += "E{0:.4f} F{1:d}\n".format(cmd['E'], cmd['F'])
        else:
            code += "{} ".format(cmd['cmd'])
            for key in cmd.keys():
                if key != 'cmd':
                    code += "{0:s}{1:d} ".format(key, cmd[key])
                    code += "\n"
        if 'layer' in cmd:
            gcode += "\n"
            gcode += "G1 E-1.0 F1200\n"
            gcode += "G1 Z8.0 E0.0 F3000\n"

        gcode += code


    return gcode


def points_to_gcode(points,
                    Z_OFFSET=Z_OFFSET_DEFAULT,
                    n_layers=N_LAYERS,
                    layer_thickness_default= LAYER_THICKNESS_DEFAULT,
                    F_default= F_DEFAULT,
                    E_ratio_default= 1.0,
                   fan_default=[255, 255, 255,255,255, 255],
                    ):
    layer_thickness = [layer_thickness_default] * n_layers
    E_ratio = [E_RATIO_DEFAULT * E_ratio_default] * n_layers
    F = [F_default] * n_layers
    fan = [255] * n_layers

    cmds = points_to_cmds(points=points,
                   Z_OFFSET=Z_OFFSET,
                   n_layers=n_layers,
                   layer_thickness_default=layer_thickness,
                   E_ratio_default=E_ratio,
                   F_default=F,
                   fan_default=fan
                    )
    gcode = cmds_to_gcode(cmds)
    return gcode
