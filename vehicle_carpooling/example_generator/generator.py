# vehicle_carpooling/exmaple_generator/generator.py

"""Example generator
"""

import numpy as np


def generate_manhattan_path_map(nb_nodes):
    """Generate a square path map

    nb_nodes (int): number of total nodes (must be a square number)
    """
    nb_side_nodes = np.sqrt(nb_nodes)
    if nb_nodes // nb_side_nodes != nb_side_nodes:
        raise ValueError("nb_nodes must be a square number")
    nb_side_nodes = int(nb_side_nodes)
    path_map = np.zeros((nb_nodes, nb_nodes))
    for i in range(nb_nodes):
        path_map[i, i] = 1
        if i % nb_side_nodes != nb_side_nodes - 1:
            path_map[i, i+1] = 1
            path_map[i+1, i] = 1
        if i < nb_nodes - nb_side_nodes:
            path_map[i, i + nb_side_nodes] = 1
            path_map[i + nb_side_nodes, i] = 1
    return path_map


def generate_start_finish_nodes(nb_entity, nb_nodes):
    """Generate start and finish nodes

    nb_entity (int): number of entities
    nb_nodes (int): number of total nodes (must be a square number)
    """
    start_node = [np.random.randint(0, nb_nodes) for _ in range(nb_entity)]
    finish_node = [np.random.randint(0, nb_nodes) for _ in range(nb_entity)]
    while sum([start_node[i] == finish_node[i] for i in range(nb_entity)]):
        finish_node = [np.random.randint(0, nb_nodes)
                       for _ in range(nb_entity)]
    return np.array(start_node), np.array(finish_node)
