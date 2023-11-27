# tests/test_utils.py

import unittest

import numpy as np

from tests.utils import matrix_utils

NB_STEPS = 2
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
            [[0, 0], [1, 0], [0, 0], [0, 0]],
            [[0, 0], [0, 1], [0, 0], [0, 0]],
            [[0, 0], [0, 0], [0, 0], [0, 0]],
            [[0, 0], [0, 0], [0, 0], [0, 0]]
        ], [
            [[0, 0], [0, 0], [0, 0], [0, 0]],
            [[0, 0], [1, 0], [0, 1], [0, 0]],
            [[0, 0], [0, 0], [0, 0], [0, 0]],
            [[0, 0], [0, 0], [0, 0], [0, 0]]
        ]])
        self.assertTrue(np.array_equal(matrix, expected_matrix))
