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

def svg2points(path):
    ifile = ET.parse(path)
    root = ifile.getroot()
    points = []
    p_prev = []
    print(2)

    for child in root.getchildren():
        print(child.tag, child.attrib)
        if child.tag[-4:] != "line":
            continue
        p1 = [child.attrib['x1'], child.attrib['y1']]
        p2 = [child.attrib['x2'], child.attrib['y2']]

        if len(p_prev) != 0:
            if dist2(p_prev, p2) > dist2(p_prev, p1):
                p3 = copy.deepcopy(p1)
                p1 = copy.deepcopy(p2)
                p2 = copy.deepcopy(p3)

        p_prev = p2

        points.append({
            'x': float(p1[0]),
            'y': float(p1[1])
        })
        points.append({
            'x': float(p2[0]),
            'y': float(p2[1])
        })



    return points


# %% main
for path in os.listdir():
    if path.split(".")[-1] == "svg":
        points = svg2points(path)
        ofile = open(path.split(".")[0] + ".gcode", "w")
        gcode = points_to_gcode(points, z_offset, n_layers, layer_thickness, printing_speed, extrusion_ratio)
        ofile.write(gcode)
        ofile.close()

# scale(points, print_gap / v_gap)
# translate(points_new, translation)
