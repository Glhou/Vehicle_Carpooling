# tests/solution_test.py

""" Solution class tests
"""

import unittest
import copy
import numpy as np


from vehicle_carpooling import solution

# Object arguments for tests
NB_STEPS = 2
NB_NODES = 4
NB_ENTITY = 2
"""
  0
 / \
1 - 2
 \ /
  3
"""
PATH_MAP = np.array([[1, 1, 1, 0],
                    [1, 1, 1, 1],
                    [1, 1, 1, 1],
                    [0, 1, 1, 1]])


class TestSolution(unittest.TestCase):
    """ Solution class tests
    """

    def test_rate_shuffle(self):
        """ Shuffle_rate_test
        Tests:
            - the difference is less than rate
            - the shuffle is the same for rate == 0
        """
        sol = solution.Solution(NB_STEPS, NB_NODES, NB_ENTITY)
        save_sol = solution.Solution(NB_STEPS, NB_NODES, NB_ENTITY)
        sol.shuffle(0, PATH_MAP)
        self.assertTrue(np.all(sol.solution == save_sol.solution))
        sol.shuffle(0.5, PATH_MAP)
        self.assertTrue(
            np.all(np.abs(save_sol.solution - sol.solution) <= 0.5))

    def test_shuffle(self):
        """Shuffle_test
        Tests:
            -  the value is between 0 and 1
            - shuffle with extreme value 1,1,1
        """
        sol = solution.Solution(NB_STEPS, NB_NODES, NB_ENTITY)
        self.assertTrue(np.all(sol.solution >= 0))
        self.assertTrue(np.all(sol.solution <= 1))
        sol = solution.Solution(1, 1, 1)
        sol.shuffle(1, np.array([[1]]))


if __name__ == '__main__':
    unittest.main()
