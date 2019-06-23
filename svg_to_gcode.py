import sys
import os
import json
import xml.etree.ElementTree as ET
import copy

# sys.path.append("/Users/Roll/Riceroll/repository/code/")
from gcoder import *


z_offset = 0.0
n_layers = 2
layer_thickness = 0.1
printing_speed = 3000
extrusion_ratio = 1.0
try:
    cfile = open("config.txt", "r")
    content = cfile.read()
    config = json.loads(content)
    z_offset = config["z_offset"]
    n_layers = config["n_layers"]
    layer_thickness = config["layer_thickness"]
    printing_speed = config["printing_speed"]
    extrusion_ratio = config["extrusion_ratio"]
except:
    print("error: config.txt is invalid.")

# %% premain


def dist2(p1, p2):
    return (p1[0] - p2[0]) * (p1[0] - p2[0] ) + (p1[1] - p2[1]) * (p1[1] - p2[1])


def center(points):
    sum = [0, 0]
    for p in points:
        sum[0] += p['x']
        sum[1] += p['y']
    avg = [sum[0] / len(points), sum[1] / len(points)]
    for i, p in enumerate(points):
        points[i]['x'] -= avg[0]
        points[i]['x'] /= 2
        points[i]['y'] -= avg[1]
        points[i]['y'] /= 2


    return points


def svg2points(path):
    ifile = ET.parse(path)
    root = ifile.getroot()
    points = []
    p_prev = []

    for child in root.getchildren():
        print(1,child.tag, child.attrib)

        if "line" not in child.tag and "polygon" not in child.tag:    # not line or polyline
            continue

        if child.tag[-8:] != "polyline" and child.tag[-7:] != "polygon":    # it is line
            p1 = [float(child.attrib['x1']), float(child.attrib['y1'])]
            p2 = [float(child.attrib['x2']), float(child.attrib['y2'])]

            if len(p_prev) != 0:
                if dist2(p_prev, p2) < dist2(p_prev, p1):
                    p3 = copy.deepcopy(p1)
                    p1 = copy.deepcopy(p2)
                    p2 = copy.deepcopy(p3)

            p_prev = p2

            points.append({
                'x': p1[0],
                'y': p1[1]
            })
            points.append({
                'x': p2[0],
                'y': p2[1]
            })
        else:   # polyline
            ps = child.attrib['points'].split()
            ps = [ [float(p.split(',')[0]), float(p.split(',')[1])] for p in ps]
            ps_new = []
            for i, p in enumerate(ps):
                ps_new.append(p)
                if i == 0:
                    continue
                if i == len(ps)-1:
                    continue
                ps_new.append(p)

            for p in ps_new:
                points.append({
                    'x': p[0],
                    'y': p[1]
                })

    return points


# %% main
for path in os.listdir():
    if path.split(".")[-1] == "svg":
        points = svg2points(path)
        points = center(points)
        ofile = open(path.split(".")[0] + ".gcode", "w")
        gcode = points_to_gcode(points, z_offset, n_layers, layer_thickness, printing_speed, extrusion_ratio)
        ofile.write(gcode)
        ofile.close()
