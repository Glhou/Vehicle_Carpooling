# tests/test_utils.py

import unittest

import numpy as np

from vehicle_carpooling.utils import paths, trees

#   0
#  / \
# 1 - 2
# \ /
#  3

PATH_MAP = np.array([[1, 1, 1, 0],
                     [1, 1, 1, 1],
                     [1, 1, 1, 1],
                     [0, 1, 1, 1]])


class TestTreeUtils(unittest.TestCase):
    """Tests for tree utils
    """

    def test_get_nodes(self):
        """Tests get nodes function
        """
        next_nodes = paths.get_next_nodes(PATH_MAP)
        supposed_next_nodes = {
            0: [0, 1, 2],
            1: [0, 1, 2, 3],
            2: [0, 1, 2, 3],
            3: [1, 2, 3]
        }
        self.assertEqual(next_nodes, supposed_next_nodes)

    def test_compute_solutions(self):
        """Tests compute solutions function
        """
        start_point = 1
        finish_point = 2
        next_nodes = {
            0: [0, 1, 2],
            1: [0, 1, 2, 3],
            2: [0, 1, 2, 3],
            3: [1, 2, 3]
        }
        nb_steps = 2
        supposed_solutions = [
            [[1, 2], [2, 2]],
            [[1, 0], [0, 2]],
            [[1, 3], [3, 2]],
            [[1, 1], [1, 2]]
        ]
        solutions = trees.compute_solutions(
            start_point, finish_point, nb_steps, next_nodes)
        supposed_solutions.sort()
        solutions.sort()
        print(supposed_solutions)
        print(solutions)
        self.assertEqual(supposed_solutions, solutions)

    def test_new_compute_trips(self):
        start_point = 1
        finish_point = 2
        nb_steps = 2
        next_nodes = {
            0: [0, 1, 2],
            1: [0, 1, 2, 3],
            2: [0, 1, 2, 3],
            3: [1, 2, 3]
        }
        expected_paths = [
            [1, 0, 2],
            [1, 1, 2],
            [1, 2],
            [1, 3, 2]
        ]
        actual_paths = list(
            trees.new_rec_compute_trips(start_point, finish_point, nb_steps, next_nodes))
        expected_paths.sort()
        actual_paths.sort()
        self.assertEqual(actual_paths, expected_paths)

    def test_compute_tree_trips(self):
        """Tests compute tree trips funciton
        """
        start_point = 0
        finish_point = 3
        next_nodes = {
            0: [0, 1, 2],
            1: [0, 1, 2, 3],
            2: [0, 1, 2, 3],
            3: [1, 2, 3]
        }
        """
    0                                              0
                                                  /|\
    1    0                                          1                                  2
        /|\                                       /||\                               /||\
    2  0        1        2          0     1        2         3           0        1       2         3
       |\      /|\      /|\         |\   /|\      /|\                    |\      /|\     /|\       
    3  1 2    1 2 3    1 2 3        1 2 1 2 3    1 2 3                   1 2    1 2 3   1 2 3 
       | |    | |      | |          | | | |      | |                     | |    | |     | |
    4  3 3    3 3      3 3          3 3 3 3      3 3                     3 3    3 3     3 3
        """
        tree_1 = []
        tree_2 = [
            0,
            [1, [3]],
            [2, [3]]
        ]
        tree_3 = [
            0,
            [0,
             [1, [3]],
             [2, [3]]
             ],
            [1,
             [1, [3]],
             [2, [3]],
             [3]
             ],
            [2,
             [1, [3]],
             [2, [3]],
             [3]
             ],
        ]
        tree_4 = [
            0,
            [0,
             [0,
              [1, [3]],
              [2, [3]]
              ],
             [1,
              [1, [3]],
              [2, [3]],
              [3]
              ],
             [2,
              [1, [3]],
              [2, [3]],
              [3]
              ]
             ],
            [1,
             [1,
                 [1, [3]],
                 [2, [3]],
                 [3]
              ],
             [2,
                 [2, [3]],
                 [3]
              ],
             [3]],
            [2,
             [1,
              [1, [3]],
              [3]
              ],
             [2,
              [1, [3]],
              [2, [3]],
              [3]
              ],
             [3]]
        ]
        steps_1 = 1
        self.assertEqual(trees.compute_tree_trips(
            start_point, finish_point, steps_1, next_nodes), tree_1)
        steps_2 = 2
        self.assertEqual(trees.compute_tree_trips(
            start_point, finish_point, steps_2, next_nodes), tree_2)
        steps_3 = 3
        self.assertEqual(trees.compute_tree_trips(
            start_point, finish_point, steps_3, next_nodes), tree_3)
        steps_4 = 4
        self.assertEqual(trees.compute_tree_trips(
            start_point, finish_point, steps_4, next_nodes), tree_4)

    def test_get_solution_from_tree(self):
        """Tests get solution from tree function"""
        tree = [
            0,
            [1, [3]],
            [2, [3]]
        ]
        tree_path_1 = [1, 1]
        tree_path_2 = [2, 1]
        sol_1 = [[0, 1], [1, 3]]
        sol_2 = [[0, 2], [2, 3]]
        self.assertEqual(trees.get_solution_from_tree(
            tree, tree_path_1), sol_1)
        self.assertEqual(trees.get_solution_from_tree(
            tree, tree_path_2), sol_2)

    def test_get_tree_neighbor(self):
        """Tests get tree neighbor function
        """
        tree_2 = [
            0,
            [1, [3]],
            [2, [3]]
        ]
        tree_path_2 = [1, 1]
        neighbor_tree_path_2 = trees.get_tree_neighbor(tree_2, tree_path_2, 0)
        self.assertEqual(neighbor_tree_path_2, [2, 1])

        tree_y = [
            0,
            [1,
             [1,
              [3]
              ],
             [2,
              [3]
              ]
             ],
            [3]
        ]
        tree_path_y = [2]
        neighbor_tree_path_y = trees.get_tree_neighbor(tree_y, tree_path_y, 0)
        self.assertTrue(neighbor_tree_path_y == [
                        1, 1, 1] or neighbor_tree_path_y == [1, 2, 1])

    def test_get_all_tree_paths(self):
        """Test private function get all tree paths
        """
        tree = [
            0,
            [1,
             [1,
              [3]
              ],
             [2,
              [3]
              ]
             ],
            [3]
        ]
        tree_paths = trees.get_all_tree_paths(tree)
        supposed_tree_paths = [
            [1, 1, 1],
            [1, 2, 1],
            [2]
        ]
        self.assertEqual(tree_paths, supposed_tree_paths)

    def test_get_all_solutions_from_tree(self):
        """Test private function get all solutions from tree
            """
        tree = [
            0,
            [1,
             [1,
              [3]
              ],
             [2,
              [3]
              ]
             ],
            [3]
        ]
        solutions = trees.get_all_solutions_from_tree(tree)
        supposed_solutions = [
            [0, 1, 1, 3],
            [0, 1, 2, 3],
            [0, 3]
        ]
        self.assertEqual(solutions, supposed_solutions)
