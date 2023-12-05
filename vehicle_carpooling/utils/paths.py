# vehicle_carpooling/utils/paths.py

"""Utils for paths
"""

import numpy as np


def get_paths(path_map):
    """Return all possible paths from the map
    """
    paths = []
    for i in range(len(path_map)):
        for j in range(len(path_map[i])):
            if path_map[i][j] == 1:
                paths.append((i, j))
    return paths


def get_next_paths(path_map):
    """Return all possible paths from the node on the map
    """
    paths = []
    for node in range(len(path_map)):
        paths[node] = []
        for i in range(len(path_map)):
            if path_map[node][i] == 1:
                paths[node].append((node, i))
    return paths
