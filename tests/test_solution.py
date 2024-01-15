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
# 1 - 2
# \ /
#  3

PATH_MAP = np.array([[1, 1, 1, 0],
                    [1, 1, 1, 1],
                    [1, 1, 1, 1],
                    [0, 1, 1, 1]])
PASSENGER_START_POINTS = np.array([0, 1])
PASSENGER_FINISH_POINTS = np.array([1, 2])
VEHICLE_START_POINTS = np.array([0, 1])

RIDE_PATH_PARAM = {
    "nb_steps": NB_STEPS,
    "nb_nodes": NB_NODES,
    "nb_passengers": NB_PASSENGERS,
    "passenger_start_points": PASSENGER_START_POINTS,
    "passenger_finish_points": PASSENGER_FINISH_POINTS,
    "path_map": PATH_MAP,
    "nb_vehicles": NB_VEHICLES,
    "vehicle_capacity": VEHICLE_CAPACITY
}

RIDE_VEHICLE_PARAM = {
    "nb_steps": NB_STEPS,
    "nb_nodes": NB_NODES,
    "nb_passengers": NB_PASSENGERS,
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
    ...


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
        ride = solution.RidePath(**RIDE_PATH_PARAM)
        # passenger 0 and 1 start and finish in their positions
        ride.solution = matrix_u.make_matrix(
            [[(0, 0, 1), (1, 1, 1)], [(0, 1, 1), (1, 1, 2)]])
        self.assertTrue(ride.check_constraint(
            True, False, False, False))
        # passenger 0 start but do not finish in good position, 1 does
        ride.solution = matrix_u.make_matrix(
            [[(0, 0, 1), (1, 1, 2)], [(0, 1, 1), (1, 1, 2)]])
        self.assertFalse(ride.check_constraint(
            True, False, False, False))
        # passenger 0 don't start in good position but finish in good position and 1 does good
        ride.solution = matrix_u.make_matrix(
            [[(0, 1, 1), (1, 1, 1)], [(0, 1, 1), (1, 1, 2)]])
        self.assertFalse(ride.check_constraint(
            True, False, False, False))
        # passenger 0 is not starting nor finishing in good positions
        ride.solution = matrix_u.make_matrix(
            [[(0, 3, 1), (1, 3, 2)], [(0, 1, 1), (1, 1, 2)]])
        self.assertFalse(ride.check_constraint(
            True, False, False, False))

    def test_path_constraint(self):
        """Check the path constraint

        Tests:
            - If passenger is on path then true
            - If passenger is not on path then false
        """
        ride = solution.RidePath(**RIDE_PATH_PARAM)
        # passenger 0 and 1 are on path
        ride.solution = matrix_u.make_matrix(
            [[(0, 0, 1), (1, 1, 1)], [(0, 1, 1), (1, 1, 2)]])
        self.assertTrue(ride.check_constraint(
            False, True, False, False))
        # passenger 0 is not on path
        ride.solution = matrix_u.make_matrix(
            [[(0, 0, 3), (1, 3, 1)], [(0, 1, 1), (1, 1, 2)]])
        self.assertFalse(ride.check_constraint(
            False, True, False, False))

    def test_continuous_constraint(self):
        """Check if the path are continuous

        Tests:
            - If path is continuous then true
            - If path is not continuous then false
        """
        passenger_finish_points = np.array([3, 1])
        ride_param = RIDE_PATH_PARAM.copy()
        ride_param["passenger_finish_points"] = passenger_finish_points
        ride = solution.RidePath(**RIDE_PATH_PARAM)
        # passenger 0 and 1 have continuous paths
        ride.solution = matrix_u.make_matrix(
            [[(0, 0, 1), (1, 1, 3)], [(0, 1, 1), (1, 1, 2)]])
        self.assertTrue(ride.check_constraint(
            False, False, True, False))
        # passenger 0 is not continuous
        ride.solution = matrix_u.make_matrix(
            [[(0, 0, 0), (1, 2, 3)], [(0, 1, 1), (1, 1, 2)]])
        self.assertFalse(ride.check_constraint(
            False, False, True, False))

    def test_vehicle_limit_constraint(self):
        """Check if the number of vehicle is under the limit
        Tests:
            - If number of vehicle is under the limit then true
            - If number of vehicle is over the limit then false
        """
        ride = solution.RidePath(**RIDE_PATH_PARAM)
        # 1 vehicles
        ride.solution = matrix_u.make_matrix(
            [[(0, 0, 1), (1, 1, 1)], [(0, 1, 1), (1, 1, 2)]])
        self.assertTrue(ride.check_constraint(
            False, False, False, True))
        # 2 vehicles
        ride.solution = matrix_u.make_matrix(
            [[(0, 0, 1), (1, 1, 1)], [(0, 1, 2), (1, 2, 2)]])
        self.assertFalse(ride.check_constraint(
            False, False, False, True))


class TestRideVehicle(unittest.TestCase):
    """RideVehicle class tests
    """

    def test_ride_link_constraint(self):
        """Check that passenger are in a car only if they use this path

        Tests:
            - If passenger are in a car and they use the path then true
            - If passenger are in a car and don't use the path then false
        """
        ride_path = solution.RidePath(**RIDE_PATH_PARAM)
        ride_vehicle = solution.RideVehicle(**RIDE_VEHICLE_PARAM)
        # passenger 0 and 1 are using the paths one after the other with the same car
        ride_path.solution = matrix_u.make_matrix(
            [[(0, 0, 1), (1, 1, 1)], [(0, 1, 1), (1, 1, 2)]])
        ride_vehicle.solution = matrix_u.make_vehicle_matrix(
            [[(0, 0)], [(1, 1)]]
        )

        self.assertTrue(ride_vehicle.check_constraint(
            ride_path, None, True, False, False, False))
        # passenger 0 is using no car but using the path
        ride_vehicle.solution = matrix_u.make_vehicle_matrix(
            [[(1, 1)]]
        )
        self.assertFalse(ride_vehicle.check_constraint(
            ride_path, None, True, False, False, False))

    def test_vehicle_number_link_constraint(self):
        """Check if vehicle number in RideVehicle is the same as in RidePath

        Tests:
            - If vehicle number in RideVehicle is the same as in RidePath then true
            - If vehicle number in RideVehicle is not the same as in RidePath then false
        """
        vehicle_capacity = 2
        nb_passengers = 3
        s_matrix_u = matrix_utils.MatrixUtils(
            NB_STEPS, NB_NODES, nb_passengers)
        ride_path_param = RIDE_PATH_PARAM.copy()
        ride_path_param["nb_passengers"] = nb_passengers
        ride_path_param["vehicle_capacity"] = vehicle_capacity
        ride_vehicle_param = RIDE_VEHICLE_PARAM.copy()
        ride_vehicle_param["vehicle_capacity"] = vehicle_capacity
        ride_vehicle_param["nb_passengers"] = nb_passengers
        ride_path = solution.RidePath(**ride_path_param)
        ride_vehicle = solution.RideVehicle(**ride_vehicle_param)
        # passenger 0 and 1 are using the paths one after the other with the same car
        ride_path.solution = s_matrix_u.make_matrix(
            [[(0, 0, 1), (1, 1, 1)], [(0, 0, 1), (1, 1, 2)], [(0, 1, 2), (1, 2, 3)]])
        ride_vehicle.solution = s_matrix_u.make_vehicle_matrix(
            [[(0, 0)],
             [(0, 0), (1, 0)],
             [(0, 1), (1, 1)]]
        )
        self.assertTrue(ride_vehicle.check_constraint(
            ride_path, None, False, True, False, False))
        # vehicle 0 is missing passenger 1 at step 0 => the number of vehicle is not affected
        ride_path.solution = s_matrix_u.make_matrix(
            [[(0, 0, 1), (1, 1, 1)], [(0, 1, 1), (1, 1, 2)], [(0, 1, 2), (1, 2, 3)]])
        ride_vehicle.solution = s_matrix_u.make_vehicle_matrix(
            [[(0, 0)],
             [(1, 0)],
             [(0, 1), (1,  1)]]
        )
        self.assertTrue(ride_vehicle.check_constraint(
            ride_path, None, False, True, False, False))
        # veicle 0 is getting one more passenger at step 0
        ride_path.solution = s_matrix_u.make_matrix(
            [[(0, 0, 1), (1, 1, 1)], [(0, 0, 1), (1, 1, 2)], [(0, 0, 1), (1, 1, 3)]])
        ride_vehicle.solution = s_matrix_u.make_vehicle_matrix(
            [[(0, 0)],
             [(0, 0), (1, 0)],
             [(0, 0), (1, 1)]]
        )
        self.assertFalse(ride_vehicle.check_constraint(
            ride_path, None, False, True, False, False))

    def test_vehicle_capacity_constraint(self):
        """Check if the capacity of the vehicle is not exeeded

        Tests:
            - If the capacity of the vehicle is not exeeded then true
            - If the capacity of the vehicle is exeeded then false
        """
        ride_vehicle = solution.RideVehicle(**RIDE_VEHICLE_PARAM)
        # vehicle 0 is not exeeding the capacity at step 0
        ride_vehicle.solution = matrix_u.make_vehicle_matrix(
            [[(0, 0)]]
        )
        self.assertTrue(ride_vehicle.check_constraint(
            None, None, False, False, True, False))
        # vehicle 0 is exeeding the capacity
        ride_vehicle.solution = matrix_u.make_vehicle_matrix(
            [[(0, 0)], [(0, 0)]]
        )
        self.assertFalse(ride_vehicle.check_constraint(
            None, None, False, False, True, False))

    def test_vehicle_in_one_edge_constraint(self):
        """Check if all vehicles are only in one edge at each steps

        Tests:
            - If all vehicles are only in one edge at each steps then true
            - If all vehicles are in several edge at any steps then false
        """
        ride_vehicle = solution.RideVehicle(**RIDE_VEHICLE_PARAM)
        ride_path = solution.RidePath(**RIDE_PATH_PARAM)
        drive = solution.Drive(**DRIVE_PARAM)
        # vehicle 0 is only in one edge at each steps
        ride_path.solution = matrix_u.make_matrix(
            [[(0, 0, 1), (1, 1, 1)], [(0, 0, 1), (1, 1, 1)]]
        )
        ride_vehicle.solution = matrix_u.make_vehicle_matrix(
            [[(0, 0)],
             [(0, 0)]]
        )
        drive.solution = matrix_u.make_matrix(
            [[(0, 0, 1), (1, 1, 2)]]
        )
        self.assertTrue(ride_vehicle.check_constraint(
            ride_path, drive, False, False, False, True))
        # vehicle 0 is in several edge at step 0
        ride_path.solution = matrix_u.make_matrix(
            [[(0, 0, 1), (1, 1, 1)], [(0, 1, 2), (1, 2, 2)]]
        )
        ride_vehicle.solution = matrix_u.make_vehicle_matrix(
            [[(0, 0)], [(0, 0)]]
        )
        drive.solution = matrix_u.make_matrix(
            [[(0, 0, 1), (1, 1, 2)]]
        )
        self.assertFalse(ride_vehicle.check_constraint(
            ride_path, drive, False, False, False, True))


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
            True, False, False))
        # vehicle 0 don't start in good position but finish in good position and 1 does good
        drive.solution = matrix_u.make_matrix(
            [[(0, 1, 1), (1, 1, 1)], [(0, 1, 1), (1, 1, 2)]])
        self.assertFalse(drive.check_constraint(
            True, False, False))

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
            False, True, False))
        # vehicle 0 is not on path
        drive.solution = matrix_u.make_matrix(
            [[(0, 0, 3), (1, 3, 1)], [(0, 1, 1), (1, 1, 2)]])
        self.assertFalse(drive.check_constraint(
            False, True, False))

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
            False, False, True))
        # vehicle 0 is not continuous
        drive.solution = matrix_u.make_matrix(
            [[(0, 0, 0), (1, 2, 3)], [(0, 1, 1), (1, 1, 2)]])
        self.assertFalse(drive.check_constraint(
            False, False, True))


if __name__ == '__main__':
    unittest.main()
