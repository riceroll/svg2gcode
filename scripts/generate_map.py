import numpy as np


map = np.zeros([500, 500, 4])

center = np.array([250, 250])

for i, r in enumerate(map):
    for j, c in enumerate(r):
        pos = np.array([i, j])
        vec = pos - center
        map[i, j] = [-vec[1], vec[0], 0.2, 0]   # x_direction, y_direction, main_shrinkage, orthogonal_shrinkage

np.save('files/map_cone.npy', map)
