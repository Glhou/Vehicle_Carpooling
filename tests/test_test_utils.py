# tests/test_test_utils.py

import unittest

import numpy as np

from tests.utils import matrix_utils

NB_STEPS = 3
NB_NODES = 4
NB_ENTITY = 2


matrix_u = matrix_utils.MatrixUtils(NB_STEPS, NB_NODES, NB_ENTITY)


class TestMatrixUtils(unittest.TestCase):
    """Test for MatrixUtils
    """

    def test_make_matrix(self):
        """test the make_matrix function
        """
        matrix = matrix_u.make_matrix(
            [[(0, 0, 1), (1, 1, 1)], [(0, 1, 1), (1, 1, 2)]])
        expected_matrix = np.array([[
            [0, 1], [1, 1], [-1, -1]
        ], [
            [1, 1], [1, 2], [-1, -1]
        ]])
        self.assertTrue(np.array_equal(matrix, expected_matrix))

    def test_make_vehicle_matrix(self):
        """test the make_vehicle_matrix funciton
        """
        matrix = matrix_u.make_vehicle_matrix(
            [[(0, 0), (1,  1)], [(0,  1), (1, 0)]])
        expected_matrix = np.array([[
            0, 1, -1
        ], [
            1, 0, -1
        ]])
        self.assertTrue(np.array_equal(matrix, expected_matrix))
