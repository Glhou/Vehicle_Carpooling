# tests/test_path.py

""" path module tests
"""

import unittest
from vehicle_carpooling.path import get_direct_paths, get_closest_node
from vehicle_carpooling.node import Node


class TestGetDirectPaths(unittest.TestCase):
    """
    A - B
    |   |
    C - D
    """

    def setUp(self):
        self.path_map = {
            'A': ['B', 'C'],
            'B': ['A', 'D'],
            'C': ['A', 'D'],
            'D': ['B', 'C']
        }

    def test_direct_path(self):
        path_map = {
            'A': ['B', 'C'],
            'B': ['A', 'D'],
            'C': ['A', 'D'],
            'D': ['B', 'C']
        }
        paths = get_direct_paths('A', 'D', path_map)
        self.assertIn(['A', 'B', 'D'], paths)
        self.assertIn(['A', 'C', 'D'], paths)

    def test_no_path(self):
        path_map = {
            'A': ['B'],
            'B': ['A'],
            'C': ['D'],
            'D': ['C']
        }
        paths = get_direct_paths('A', 'D', path_map)
        self.assertEqual(paths, [])

    def test_self_path(self):
        path_map = {
            'A': ['B'],
            'B': ['A']
        }
        paths = get_direct_paths('A', 'A', path_map)
        self.assertEqual(paths, [['A']])

    def test_get_closest_node(self):
        nodes = [
            Node('A', 0, 0),
            Node('B', 1, 1),
            Node('C', 2, 2),
            Node('D', 3, 3)
        ]
        current_node = Node('E', 1.5, 1.5)
        closest_node = get_closest_node(nodes, current_node)
        self.assertEqual(closest_node.id, 'B')
