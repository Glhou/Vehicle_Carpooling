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

    def make_matrix(self, entity_paths: list[list[tuple]]) -> np.ndarray:
        """Make a matrix with desired paths

        Args:
            entity_paths (list(list(tuple))): list of entity's list of paths (tuples: step, k, l)

        Returns:
            np.ndarray: matrix with desired paths
        """
        matrix = np.array([[[-1, -1] for _ in range(self.nb_steps)]
                          for _ in range(self.nb_entity)])
        for entity, paths_list in enumerate(entity_paths):
            for path in paths_list:
                matrix[entity, path[0]] = [path[1], path[2]]
        return matrix

    def make_vehicle_matrix(self, entity_paths: list[list[tuple]]) -> np.ndarray:
        """Make a matrix with desired paths

        Args:
            entity_paths (list(list(tuple))): list of passenger's list of vehicle used (tuples: step, vehicle)

        Returns:
            np.ndarray: matrix used by RideVehicle
        """
        matrix = np.array([[-1 for _ in range(self.nb_steps)]
                          for _ in range(self.nb_entity)])
        for entity, paths in enumerate(entity_paths):
            for (step, vehicle) in paths:
                matrix[entity, step] = vehicle
        return matrix
