# tests/solution_test.py

""" Solution class tests
"""

import unittest
import copy
import numpy as np


from vehicle_carpooling import solution
from tests.utils import matrix_utils

# Object arguments for tests
NB_STEPS = 2
NB_NODES = 4
NB_PASSENGERS = 2
NB_ENTITY = 2
NB_VEHICLES = 1
VEHICLE_CAPACITY = 1

#  0
# / \
#1 - 2
# \ /
#  3

PATH_MAP = np.array([[1, 1, 1, 0],
                    [1, 1, 1, 1],
                    [1, 1, 1, 1],
                    [0, 1, 1, 1]])
PASSENGER_START_POINTS = np.array([0, 1])
PASSENGER_FINISH_POINTS = np.array([1, 2])
VEHICLE_START_POINTS = np.array([0, 1])

RIDE_PARAM = {
    "nb_steps": NB_STEPS,
    "nb_nodes": NB_NODES,
    "nb_passengers": NB_PASSENGERS,
    "passenger_start_points": PASSENGER_START_POINTS,
    "passenger_finish_points": PASSENGER_FINISH_POINTS,
    "path_map": PATH_MAP,
    "nb_vehicles": NB_VEHICLES,
    "vehicle_capacity": VEHICLE_CAPACITY
}

DRIVE_PARAM = {
    "nb_steps": NB_STEPS,
    "nb_nodes": NB_NODES,
    "nb_vehicles": NB_VEHICLES,
    "vehicle_capacity": VEHICLE_CAPACITY,
    "vehicle_start_points": VEHICLE_START_POINTS,
    "path_map": PATH_MAP
}

matrix_u = matrix_utils.MatrixUtils(NB_STEPS, NB_NODES, NB_ENTITY)


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


class TestRidePath(unittest.TestCase):
    """RidePath class tests
    """

    def test_start_finish_constraint(self):
        """Start_finish_condition_test

        Tests:
            - If passenger start and finish then true
            - If passenger start and not finish then false
            - If passenger not start and finish then false
            - If passenger not start and not finish then false
        """
        ride = solution.RidePath(**RIDE_PARAM)
        # passenger 0 and 1 start and finish in their positions
        ride.solution = matrix_u.make_matrix(
            [[(0, 0, 1), (1, 1, 1)], [(0, 1, 1), (1, 1, 2)]])
        self.assertTrue(ride.check_constraint(
            True, False, False, False, False))
        # passenger 0 start but do not finish in good position, 1 does
        ride.solution = matrix_u.make_matrix(
            [[(0, 0, 1), (1, 1, 2)], [(0, 1, 1), (1, 1, 2)]])
        self.assertFalse(ride.check_constraint(
            True, False, False, False, False))
        # passenger 0 don't start in good position but finish in good position and 1 does good
        ride.solution = matrix_u.make_matrix(
            [[(0, 1, 1), (1, 1, 1)], [(0, 1, 1), (1, 1, 2)]])
        self.assertFalse(ride.check_constraint(
            True, False, False, False, False))
        # passenger 0 is not starting nor finishing in good positions
        ride.solution = matrix_u.make_matrix(
            [[(0, 3, 1), (1, 3, 2)], [(0, 1, 1), (1, 1, 2)]])
        self.assertFalse(ride.check_constraint(
            True, False, False, False, False))

    def test_path_constraint(self):
        """Check the path constraint

        Tests:
            - If passenger is on path then true
            - If passenger is not on path then false
        """
        ride = solution.RidePath(**RIDE_PARAM)
        # passenger 0 and 1 are on path
        ride.solution = matrix_u.make_matrix(
            [[(0, 0, 1), (1, 1, 1)], [(0, 1, 1), (1, 1, 2)]])
        self.assertTrue(ride.check_constraint(
            False, True, False, False, False))
        # passenger 0 is not on path
        ride.solution = matrix_u.make_matrix(
            [[(0, 0, 3), (1, 3, 1)], [(0, 1, 1), (1, 1, 2)]])
        self.assertFalse(ride.check_constraint(
            False, True, False, False, False))

    def test_continuous_constraint(self):
        """Check if the path are continuous

        Tests:
            - If path is continuous then true
            - If path is not continuous then false
        """
        passenger_finish_points = np.array([3, 1])
        ride_param = RIDE_PARAM.copy()
        ride_param["passenger_finish_points"] = passenger_finish_points
        ride = solution.RidePath(**RIDE_PARAM)
        # passenger 0 and 1 have continuous paths
        ride.solution = matrix_u.make_matrix(
            [[(0, 0, 1), (1, 1, 3)], [(0, 1, 1), (1, 1, 2)]])
        self.assertTrue(ride.check_constraint(
            False, False, True, False, False))
        # passenger 0 is not continuous
        ride.solution = matrix_u.make_matrix(
            [[(0, 0, 0), (1, 2, 3)], [(0, 1, 1), (1, 1, 2)]])
        self.assertFalse(ride.check_constraint(
            False, False, True, False, False))

    def test_action_per_step_constraint(self):
        """Check that passenger do only one action per step
        Tests:
            - If passenger do only one action per step then true
            - If passenger do more than one action per step then false
        """
        ride = solution.RidePath(**RIDE_PARAM)
        # passenger 0 and 1 do only one action per step
        ride.solution = matrix_u.make_matrix(
            [[(0, 0, 1), (1, 1, 1)], [(0, 1, 1), (1, 1, 2)]])
        self.assertTrue(ride.check_constraint(
            False, False, False, True, False))
        # passenger 0 do more than one action per step
        ride.solution = matrix_u.make_matrix(
            [[(0, 0, 1), (0, 0, 2), (1, 1, 1)], [(0, 1, 1), (1, 1, 2)]])
        self.assertFalse(ride.check_constraint(
            False, False, False, True, False))

    def test_vehicle_limit_constraint(self):
        """Check if the number of vehicle is under the limit
        Tests:
            - If number of vehicle is under the limit then true
            - If number of vehicle is over the limit then false
        """
        ride = solution.RidePath(**RIDE_PARAM)
        # 1 vehicles
        ride.solution = matrix_u.make_matrix(
            [[(0, 0, 1), (1, 1, 1)], [(0, 1, 1), (1, 1, 2)]])
        self.assertTrue(ride.check_constraint(
            False, False, False, False, True))
        # 2 vehicles
        ride.solution = matrix_u.make_matrix(
            [[(0, 0, 1), (1, 1, 1)], [(0, 1, 2), (1, 2, 2)]])
        self.assertTrue(ride.check_constraint(
            False, False, False, False, True))


class TestDrive(unittest.TestCase):
    """Drive class tests
    """

    def test_vehicle_start_constraint(self):
        """Check vehicle start constraint

        Tests:
            - If vehicle start then true
            - If vehicle do not start then false
        """
        drive = solution.Drive(**DRIVE_PARAM)
        # vehicle 0 and 1 start and finish in their positions
        drive.solution = matrix_u.make_matrix(
            [[(0, 0, 1), (1, 1, 1)], [(0, 1, 1), (1, 1, 2)]])
        self.assertTrue(drive.check_constraint(
            True, False, False, False))
        # vehicle 0 don't start in good position but finish in good position and 1 does good
        drive.solution = matrix_u.make_matrix(
            [[(0, 1, 1), (1, 1, 1)], [(0, 1, 1), (1, 1, 2)]])
        self.assertFalse(drive.check_constraint(
            True, False, False, False))

    def test_path_constraint(self):
        """Check the path constraint

        Tests:
            - If vehicle is on path then true
            - If vehicle is not on path then false
        """
        drive = solution.Drive(**DRIVE_PARAM)
        # vehicle 0 and 1 are on path
        drive.solution = matrix_u.make_matrix(
            [[(0, 0, 1), (1, 1, 1)], [(0, 1, 1), (1, 1, 2)]])
        self.assertTrue(drive.check_constraint(
            False, True, False, False))
        # vehicle 0 is not on path
        drive.solution = matrix_u.make_matrix(
            [[(0, 0, 3), (1, 3, 1)], [(0, 1, 1), (1, 1, 2)]])
        self.assertFalse(drive.check_constraint(
            False, True, False, False))

    def test_continuous_constraint(self):
        """Check if the path are continuous

        Tests:
            - If path is continuous then true
            - If path is not continuous then false
        """
        drive = solution.Drive(**DRIVE_PARAM)
        # vehicle 0 and 1 have continuous paths
        drive.solution = matrix_u.make_matrix(
            [[(0, 0, 1), (1, 1, 3)], [(0, 1, 1), (1, 1, 2)]])
        self.assertTrue(drive.check_constraint(
            False, False, True, False))
        # vehicle 0 is not continuous
        drive.solution = matrix_u.make_matrix(
            [[(0, 0, 0), (1, 2, 3)], [(0, 1, 1), (1, 1, 2)]])
        self.assertFalse(drive.check_constraint(
            False, False, True, False))

    def test_action_per_step_constraint(self):
        """Check that vehicle do only one action per step
        Tests:
            - If vehicle do only one action per step then true
            - If vehicle do more than one action per step then false
        """
        drive = solution.Drive(**DRIVE_PARAM)
        # vehicle 0 and 1 do only one action per step
        drive.solution = matrix_u.make_matrix(
            [[(0, 0, 1), (1, 1, 1)], [(0, 1, 1), (1, 1, 2)]])
        self.assertTrue(drive.check_constraint(
            False, False, False, True))
        # vehicle 0 do more than one action per step
        drive.solution = matrix_u.make_matrix(
            [[(0, 0, 1), (0, 0, 2), (1, 1, 1)], [(0, 1, 1), (1, 1, 2)]])
        self.assertFalse(drive.check_constraint(
            False, False, False, True))


if __name__ == '__main__':
    unittest.main()
