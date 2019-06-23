import numpy as np
from pyroll import pygl


class Vertex:
    def __init__(self, x, y, index):
        self.pos = np.array([x, y])
        self.edges = [None, None, None, None, None, None]
        self.index = index


class Edge:
    def __init__(self, v1, v2):
        self.v1 = v1    # topper or lefter than v2
        self.v2 = v2
        self.vec = v2.pos - v1.pos
        self.centroid = (v1.pos + v2.pos) / 2
        self.l = pygl.get_norm(self.vec)
        self.shrinkage = .0


class Mesh:
    def __init__(self, n_vertical_vertices=5, n_horizontal_vertices=6, column_height=1):
        self.m = n_vertical_vertices
        self.n = n_horizontal_vertices
        self.l = column_height / np.sqrt(3) * 2

        self.width = (self.n - 0.5) * self.l
        self.height = self.l * (np.sqrt(3) / 2) * (self.m - 1)

        self.vertices = []
        self.edges = []
        index = 0
        for r in range(self.m):
            for c in range(self.n):
                x = c * self.l + self.l/2 if r % 2 else c * self.l
                y = r * self.l * np.sqrt(3) / 2
                v = Vertex(x, y, index)
                index += 1
                self.vertices.append(v)

        for r in range(self.m):
            for c in range(self.n):
                i1 = r * self.n + c
                # horizontal
                if c != self.n - 1:     # not last col
                    i2 = i1 + 1
                    e = Edge(self.vertices[i1], self.vertices[i2])
                    self.edges.append(e)
                    self.vertices[i1].edges[0] = e
                    self.vertices[i2].edges[3] = e
                if r != self.m - 1:  # not last row
                    if r % 2:   # odd
                        # left_bottom
                        i2 = i1 + self.n
                        e = Edge(self.vertices[i1], self.vertices[i2])
                        self.edges.append(e)
                        self.vertices[i1].edges[4] = e
                        self.vertices[i2].edges[1] = e
                        # right_bottom
                        if c != self.n - 1:  # not last col
                            i3 = i2 + 1
                            e = Edge(self.vertices[i1], self.vertices[i3])
                            self.edges.append(e)
                            self.vertices[i1].edges[5] = e
                            self.vertices[i3].edges[2] = e
                    else:   # even
                        # right_bottom
                        i2 = i1 + self.n
                        e = Edge(self.vertices[i1], self.vertices[i2])
                        self.edges.append(e)
                        self.vertices[i1].edges[5] = e
                        self.vertices[i2].edges[2] = e
                        # left_bottom
                        if c != 0:  # not first col
                            i3 = i2 - 1
                            e = Edge(self.vertices[i1], self.vertices[i3])
                            self.edges.append(e)
                            self.vertices[i1].edges[4] = e
                            self.vertices[i3].edges[1] = e

    def print(self):
        points = []

        direction = 'r'
        v = self.vertices[0]
        points.append([v.pos[0], v.pos[1], 0, 0])
        while True:
            # print(direction, v.index)
            if direction == 'r':    # right
                if v.edges[0]:   # has right
                    e = v.edges[0]
                    v = e.v2
                else:   # no right
                    if v.edges[5]:      # has right_bottom
                        v = v.edges[5].v2
                        direction = 'l'
                    elif v.edges[4]:    # has left_bottom
                        v = v.edges[4].v2
                        direction = 'l'
                    else:
                        direction = 'rt'
                    points.append([v.pos[0], v.pos[1], 0, 0.5])
                    continue

            elif direction == 'l':      # left
                if v.edges[3]:  # has left
                    e = v.edges[3]
                    v = e.v1
                else:   # no left
                    if v.edges[4]:  # has left_bottom
                        v = v.edges[4].v2
                        direction = 'r'
                    elif v.edges[5]:  # has right_bottom
                        v = v.edges[5].v2
                        direction = 'r'
                    else:
                        v = self.vertices[-1]
                        direction = 'rt'
                    points.append([v.pos[0], v.pos[1], 0, 0.5])
                    continue

            elif direction == 'rt':     # right_top
                if v.edges[1]:  # has top_right
                    e = v.edges[1]
                    v = self.vertices[e.v1.index]
                else:   # no top_right
                    if v.edges[2]:  # has top_left
                        if v.edges[2].v1.edges[1]:  # has top_top
                            v = v.edges[2].v1.edges[1].v1   # top_top
                            direction = 'lb'
                        else:   # no top_top
                            v = v.edges[2].v1   # top_left
                            direction = 'lb'
                    else:
                        if v.edges[3]:  # has left
                            v = v.edges[3].v1  # left
                            direction = 'lb'
                        else:
                            v = self.vertices[self.n - 1]   # last of the first column
                            direction = 'rb'
                    points.append([v.pos[0], v.pos[1], 0, 0.5])
                    continue

            elif direction == 'lb':     # left_bottom
                if v.edges[4]:      # has left_bottom
                    e = v.edges[4]
                    v = e.v2
                else:   # no left_bottom
                    if v.edges[3]:  # has left
                        v = v.edges[3].v1
                        direction = 'rt'
                    else:   # no left
                        if v.edges[2]:  # has top_left
                            v = v.edges[2].v1
                            direction = 'rt'
                        elif v.edges[1]: # has top_right
                            if v.edges[1].v1.edges[2]: # has top_top
                                v = v.edges[1].v1.edges[2].v1   # top_top
                                direction = 'rt'
                            else:
                                v = self.vertices[self.n - 1]  # move to the last of the first column
                                direction = 'rb'
                        else:
                            v = self.vertices[self.n - 1]  # move to the last of the first column
                            direction = 'rb'

                    points.append([v.pos[0], v.pos[1], 0, 0.5])
                    continue

            elif direction == 'rb':     # right_bottom
                if v.edges[5]:  # has right_bottom
                    e = v.edges[5]
                    v = e.v2
                else:
                    if v.edges[4]:  # has left_bottom
                        if v.edges[4].v2.edges[5]:      # has bottom_bottom
                            v = v.edges[4].v2.edges[5].v2
                            direction = 'lt'
                        else:   # no bottom_bottom
                            v = v.edges[4].v2   # left_bottom
                            direction = 'lt'
                    else:   # not left_bottom
                        if v.edges[3]:  # has left
                            v = v.edges[3].v1
                            direction = 'lt'
                        else:
                            break

            elif direction == 'lt':     # left_top
                if v.edges[2]:  # has left_top
                    e = v.edges[2]
                    v = e.v1
                else:
                    if v.edges[3]:  # has left
                        v = v.edges[3].v1
                        direction = 'rb'
                    else:
                        if v.edges[4]:  # has left_bottom
                            v = v.edges[4].v2
                            direction = 'rb'
                        else:
                            if v.edges[5]:  # has right_bottom
                                if v.edges[5].v2.edges[4]:  # has bottom_bottom
                                    v = v.edges[5].v2.edges[4].v2
                                    direction = 'rb'
                                else:
                                    break
                            else:
                                break

            points.append([v.pos[0], v.pos[1], e.shrinkage, 1.])

        # # test
        # for point in points:
        #     print(point[0], point[1])

        return points

    def shrink(self, map_name):
        '''
        :param map_name: .npy file storing the shrinkage vector field [x, y, main_shrinkage, orthogonal shrinkage]
        :process: assign shrinkage rate to each edge
        '''

        map = np.load(str('files/' + map_name + '.npy'))
        w = map.shape[0]
        h = map.shape[1]
        for edge in self.edges:
            v = map[int(edge.centroid[0] / self.width * (w - 1)), int(edge.centroid[1] / self.height * (h - 1))]    # from edge centroid to the map
            vm = v[:2]  # main direction vector
            sa = v[2]   # main shrinkage
            sb = v[3]   # orthogonal shrinkage
            ve = edge.vec   # edge direction vector
            alpha = np.arccos(np.abs(pygl.dot(vm, ve)/pygl.get_norm(vm)/pygl.get_norm(ve)))   # angle between main vector and edge vector
            l_new = np.sqrt((np.sin(alpha) * edge.l * (1 - sb)) ** 2 + (np.cos(alpha) * edge.l * (1 - sa)) ** 2)    # new edge length
            s = (edge.l - l_new) / edge.l   # shrinkage of the edge
            edge.shrinkage = s























