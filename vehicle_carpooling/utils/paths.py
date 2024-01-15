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
    paths = dict()
    for node, path in enumerate(path_map):
        paths[node] = []
        for node_i, path_or_not in enumerate(path):
            if path_or_not:
                paths[node].append((node, node_i))
    return paths


def get_next_nodes(path_map):
    """Return a dictionnary of all legal next node on the map
    """
    next_nodes = dict()
    for node, path in enumerate(path_map):
        next_nodes[node] = []
        for next_node, path_or_not in enumerate(path):
            if path_or_not:
                next_nodes[node].append(next_node)
    return next_nodes
