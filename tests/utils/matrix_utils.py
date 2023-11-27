# tests/utils/matrix_utils.py

"""Tests utils for making matrix
"""

import numpy as np


class MatrixUtils:
    """MatrixUtils class
    """

    def __init__(self, nb_steps: int, nb_nodes: int, nb_entity: int):
        """MatrixUtils initialization

        Args:
            nb_steps (int): number of steps
            nb_nodes (int): number of nodes
            nb_entity (int): number of entity
        """
        self.nb_steps = nb_steps
        self.nb_nodes = nb_nodes
        self.nb_entity = nb_entity

    def make_matrix(self, passenger_paths: list[list[tuple]]) -> np.ndarray:
        """Make a matrix with desired paths

        Args:
            passenger_paths (list(tuple)): list of passenger's list of paths (tuples: step, k, l)

        Returns:
            np.ndarray: matrix with desired paths
        """
        matrix = np.zeros((self.nb_steps, self.nb_nodes,
                          self.nb_nodes, self.nb_entity))
        for passenger, paths_list in enumerate(passenger_paths):
            for path in paths_list:
                matrix[path[0], path[1], path[2], passenger] = 1
        return matrix
