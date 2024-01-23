# tests/generator_test.py

""" Generator module tests
"""

import unittest
import copy
import numpy as np

from vehicle_carpooling.example_generator import generator as ge


class TestGenerator(unittest.TestCase):
    """Test generator
    """

    def test_generate_manhattan_path_map(self):
        """Test generate_manhattan_path_map
        """
        nb_nodes = 16
        path_map = ge.generate_manhattan_path_map(nb_nodes)
        self.assertEqual(path_map.shape, (nb_nodes, nb_nodes))
        supposed_map = np.zeros((16, 16))
        for i in range(16):
            supposed_map[i, i] = 1
            if i % 4 != 3:
                supposed_map[i, i+1] = 1
                supposed_map[i+1, i] = 1
            if i < 12:
                supposed_map[i, i+4] = 1
                supposed_map[i+4, i] = 1
        self.assertTrue(np.array_equal(path_map, supposed_map))

    def test_generate_manhattan_path_map_non_square(self):
        """Test generate_manhattan_path_map with non-square number of nodes
        """
        nb_nodes = 15
        with self.assertRaises(Exception):
            ge.generate_manhattan_path_map(nb_nodes)
