# vehicle_carpooling/solution.py

"""Defines the Solution, Ride and Drive class
"""

import numpy as np
import math
import copy
import logging
import vehicle_carpooling.utils as utils

logger = logging.getLogger(__name__)


class Solution:
    """Solution class
    """

    def __init__(self, nb_steps, nb_nodes, nb_entity, empty_value, path_map) -> None:
        """Initialize the Solution object

        Args:
            nb_steps (int): number of maximum steps
            nb_nodes (int): number of nodes
            nb_entity (int): number of entity (passenger / vehicles)
            empty_value (int or list): value of empty
            path_map (np.ndarray): possible path on the map
        """
        self.nb_steps = nb_steps
        self.nb_nodes = nb_nodes
        self.nb_entity = nb_entity
        self.path_map = path_map
        self.paths = utils.paths.get_paths(path_map)
        self.next_paths = utils.paths.get_next_paths(path_map)
        self.next_nodes = utils.paths.get_next_nodes(path_map)
        self.empty_value = empty_value
        self.violation_count = 0
        self.solution = np.array(
            [[empty_value for _ in range(self.nb_steps)] for _ in range(self.nb_entity)])

    def _iter(self, depth=4):
        """Return iterator of indexes the solution using the solution shape

        Args:
            depth (int): depth of the iterator (ex: 1 return an iterator on step only)
        """
        if depth == 1:
            return [i[0] for i in np.ndindex(self.solution.shape[0])]
        return np.ndindex(self.solution.shape[:depth])

    def _check_violation(self, cons) -> bool:
        """Increment the violation count if bool is False
        """
        cons = bool(cons)
        if not cons:
            self.violation_count += 1
        return cons

    def _random_value(self, entity, step):
        """Return a random value of the type used in the solution
        """
        return self.empty_value

    def _initiate_shuffle(self):
        """Initiate the shuffle

        Select starting points or finish points if exists

        Return:
            list of selected steps
        """
        return []

    def shuffle(self, rate):
        """Shuffle the solution

        Args:
            rate (float): rate of shuffle
        """
        done_steps = self._initiate_shuffle()
        for entity in range(self.nb_entity):
            for step in range(self.nb_steps):
                if not step in done_steps:
                    if np.random.rand() < rate:
                        self.solution[entity, step] = self._random_value(
                            entity, step)

    def copy(self):
        return copy.deepcopy(self)

    def get_neighbor(self, rate, temperature):
        """Return a neighbor of the current solution
        """
        neighbor = self.copy()
        for entity in range(self.nb_entity):
            for step in range(self.nb_steps):
                if np.random.rand() < rate:
                    swap_node = neighbor.solution[entity, step, 1]
                    swap_node += temperature * np.random.choice([-1, 1])
                    swap_node = max(0, min(swap_node, self.nb_nodes - 1))
                    neighbor.solution[entity, step, 1] = swap_node
                    if step < self.nb_steps - 1:
                        neighbor.solution[entity, step+1, 0] = swap_node
        return neighbor


class RidePath(Solution):
    """RidePath class
    """

    def __init__(self, nb_steps: int, nb_nodes: int, nb_passengers: int, passenger_start_points: np.ndarray, passenger_finish_points: np.ndarray, path_map: np.ndarray, nb_vehicles: int, vehicle_capacity: int) -> None:
        """Initialize the RidePath object

        Args:
            nb_steps (int): number of maximum steps
            nb_nodes (int): number of nodes
            nb_passengers (int): number of passengers
            passenger_start_points (np.ndarray): passenger start points
            passenger_finish_points (np.ndarray): passenger finish points
            path_map (np.ndarray): possible path on the map
            nb_vehicles (int): number of vehicles
            vehicle_capacity (int): vehicle capacity
        """
        super().__init__(nb_steps, nb_nodes, nb_passengers, [-1, -1], path_map)
        self.passenger_start_points = passenger_start_points
        self.passenger_finish_points = passenger_finish_points
        self.nb_vehicles = nb_vehicles
        self.vehicle_capacity = vehicle_capacity
        self.trips = dict()
        self._compute_trips()

    def _compute_trips(self):
        for passenger in range(self.nb_entity):
            start_point = self.passenger_start_points[passenger]
            finish_point = self.passenger_finish_points[passenger]
            self.trips[passenger] = utils.trees.compute_trips(
                start_point, finish_point, self.nb_steps, self.next_nodes)

    def _initiate_shuffle(self):
        for passenger in range(self.nb_entity):
            start_node = self.passenger_start_points[passenger]
            start_paths = self.next_paths[start_node]
            start_path = start_paths[np.random.choice(len(start_paths))]
            self.solution[passenger, 0] = start_path
            finish_node = self.passenger_finish_points[passenger]
            finish_paths = self.next_paths[finish_node]
            finish_path = finish_paths[np.random.choice(len(finish_paths))]
            self.solution[passenger, -1] = finish_path
        return [0, -1]

    def _random_value(self, entity, step):
        previous_node = self.solution[entity, step-1, 1]
        random_legit_continuous_path = self.next_paths[previous_node][np.random.choice(
            len(self.next_paths[previous_node]))]
        return [random_legit_continuous_path[0], random_legit_continuous_path[1]]

    def _check_start_finish_constraint(self) -> bool:
        '''Constraint: Each passenger must start and finish in designated places
        '''
        check = True
        for passenger in range(self.nb_entity):
            check *= self.solution[passenger, 0,
                                   0] == self.passenger_start_points[passenger]
            check *= self.solution[passenger, -1,
                                   1] == self.passenger_finish_points[passenger]
        return self._check_violation(check)

    def _check_path_constraint(self) -> bool:
        '''Constraint: Passengers cannot be on non paths (use R and M)
        '''
        check = True
        for passenger in range(self.nb_entity):
            for step in range(self.nb_steps):
                check *= self.path_map[self.solution[passenger,
                                                     step, 0], self.solution[passenger, step, 1]]
        return self._check_violation(check)

    def _check_continuous_constraint(self) -> bool:
        '''Constraint: The path needs to be continuous
        '''
        check = True
        for passenger in range(self.nb_entity):
            for step in range(self.nb_steps-1):
                check *= self.solution[passenger, step,
                                       1] == self.solution[passenger, step+1, 0]
        return self._check_violation(check)

    def _check_limit_vehicle_constraint(self) -> bool:
        '''Constraint: There is a limited total number of vehicles at each step
        '''
        check = True
        for step in range(self.nb_steps):
            # count (not sum) the number of people that are not staying on the same node
            check *= np.count_nonzero(self.solution[:, step, 0] !=
                                      self.solution[:, step, 1]) / self.vehicle_capacity <= self.nb_vehicles
        return self._check_violation(check)

    def check_constraint(self, start_finish_constraint=True, path_constraint=True, continuous_constraint=True, limit_vehicle_constraint=True) -> bool:
        '''Constraint: All constraints

        Args:
            start_finish_constraint (bool, optional): Constraint: Each passenger must start and finish in designated places. Defaults to True.
            path_constraint (bool, optional): Constraint: Passengers cannot be on non paths (use R and M). Defaults to True.
            continuous_constraint (bool, optional): Constraint: The path needs to be continuous. Defaults to True.
            limit_vehicle_constraint (bool, optional): Constraint: There is a limited total number of vehicles at each step. Defaults to True.
        '''
        self.violation_count = 0
        check = True
        if start_finish_constraint:
            check *= self._check_start_finish_constraint()
        if path_constraint:
            check *= self._check_path_constraint()
        if continuous_constraint:
            check *= self._check_continuous_constraint()
        if limit_vehicle_constraint:
            check *= self._check_limit_vehicle_constraint()
        return check


class Drive(Solution):
    """Drive class
    """

    def __init__(self, nb_steps: int, nb_nodes: int, nb_vehicles: int, vehicle_capacity: int, vehicle_start_points: np.ndarray, path_map: np.ndarray) -> None:
        """Initialize the Drive object

        Args:
            nb_steps (int): number of maximum steps
            nb_nodes (int): number of nodes
            nb_vehicles (int): number of vehicles
            vehicle_capacity (int): vehicle capacity
            vehicle_start_points (np.ndarray): list of vehicle start points
            path_map (np.ndarray): possible path on the map
        """
        super().__init__(nb_steps, nb_nodes, nb_vehicles, [-1, -1], path_map)
        self.vehicle_capacity = vehicle_capacity
        self.vehicle_start_points = vehicle_start_points

    def _initiate_shuffle(self):
        for vehicle in range(self.nb_entity):
            start_node = self.vehicle_start_points[vehicle]
            start_paths = self.next_paths[start_node]
            start_path = start_paths[np.random.choice(len(start_paths))]
            self.solution[vehicle, 0] = start_path
        return [0]

    def _random_value(self, entity, step):
        previous_node = self.solution[entity, step-1, 1]
        random_legit_continuous_path = self.next_paths[previous_node][np.random.choice(
            len(self.next_paths[previous_node]))]
        return [random_legit_continuous_path[0], random_legit_continuous_path[1]]

    def _check_vehicle_start_constraint(self) -> bool:
        '''Constraint: Each vehicle must start at designated places
        '''
        check = True
        for vehicle in range(self.nb_entity):
            check *= self.solution[vehicle,
                                   0, 0] == self.vehicle_start_points[vehicle]
        return self._check_violation(check)

    def _check_vehicles_path_constraint(self) -> bool:
        '''Constraint: Vehicle cannot be on non paths
        '''
        check = True
        for vehicle in range(self.nb_entity):
            for step in range(self.nb_steps):
                check *= self.path_map[self.solution[vehicle,
                                                     step, 0], self.solution[vehicle, step, 1]]
        return self._check_violation(check)

    def _check_vehicles_continuous_constraint(self) -> bool:
        '''Constraint: The path needs to be continuous
        '''
        check = True
        for vehicle in range(self.nb_entity):
            for step in range(self.nb_steps-1):
                check *= self.solution[vehicle, step,
                                       1] == self.solution[vehicle, step+1, 0]
        return self._check_violation(check)

    def check_constraint(self, vehicle_start_constraint=True, vehicles_path_constraint=True, vehicles_continuous_constraint=True) -> bool:
        '''Constraint: All constraints

        Args:
            limit_vehicle_constraint (bool, optional): Constraint: There is a limited total number of vehicles at each step. Defaults to True.
            vehicle_start_constraint (bool, optional): Constraint: Each vehicle must start at designated places. Defaults to True.
            vehicles_path_constraint (bool, optional): Constraint: Vehicle cannot be on non paths. Defaults to True.
            vehicles_continuous_constraint (bool, optional): Constraint: The path needs to be continuous. Defaults to True.
        '''
        self.violation_count = 0
        check = True
        if vehicle_start_constraint:
            check *= self._check_vehicle_start_constraint()
        if vehicles_path_constraint:
            check *= self._check_vehicles_path_constraint()
        if vehicles_continuous_constraint:
            check *= self._check_vehicles_continuous_constraint()
        return check


class RideVehicle(Solution):
    """RideVehicle class
    """

    def __init__(self, nb_steps: int, nb_nodes: int, nb_passengers: int, path_map: np.ndarray, nb_vehicles: int, vehicle_capacity: int):
        """Initialize the RideVehicle object

        Args:
            nb_steps (int): number of maximum steps
            nb_nodes (int): number of nodes
            nb_passengers (int): number of passengers
            path_map (np.ndarray): possible path on the map
            nb_vehicles (int): number of vehicles
            vehicle_capacity (int): vehicle capacity
        """
        super().__init__(nb_steps, nb_nodes, nb_passengers, -1,  path_map)
        self.nb_vehicles = nb_vehicles
        self.vehicle_capacity = vehicle_capacity

    def _random_value(self, entity, step):
        return np.random.randint(0, self.nb_vehicles)

    def _check_ride_link_constraint(self, ride_path: RidePath) -> bool:
        '''Constraint: passenger use car only when they use the path and contrary
        '''
        check = True
        for step in range(self.nb_steps):
            for passenger in range(self.nb_entity):
                # the passenger is not in a vehicle or (he is in a vehicle and not still)
                check *= self.solution[passenger, step] == -1 or (
                    self.solution[passenger, step] != -1 and ride_path.solution[passenger, step, 0] != ride_path.solution[passenger, step, 1])
        return self._check_violation(check)

    def _check_vehicle_number_link_ride_constraint(self, ride_path: RidePath) -> bool:
        '''Constraint: vehicle number is the same in ridePath and rideVehicle
        '''
        check = True
        for step in range(self.nb_steps):
            step_nb_vehicle = 0
            for vehicle_id in range(self.nb_vehicles):
                step_nb_vehicle += np.count_nonzero(
                    self.solution[:, step] == vehicle_id)
            check *= step_nb_vehicle == math.ceil(np.count_nonzero(
                ride_path.solution[:, step, 0] != ride_path.solution[:, step, 1]) / self.vehicle_capacity)
        return self._check_violation(check)

    def _check_vehicle_capacity_constraint(self) -> bool:
        '''Constraint: Vehicle capacity limit
        '''
        check = True
        for step in range(self.nb_steps):
            for vehicle_id in range(self.nb_vehicles):
                check *= np.count_nonzero(self.solution[:, step]
                                          == vehicle_id) <= self.vehicle_capacity
        return self._check_violation(bool(check))

    def _check_vehicle_only_in_one_edge_condition(self, ride_path: RidePath, drive: Drive) -> bool:
        """Constraint: a vehicle can only be in a edge a a time at maximum
        """
        check = True
        for step in range(self.nb_steps):
            # check that if passengers use a vehicle at any step, then these passengers needs to be on the same path
            for vehicle_id in range(self.nb_vehicles):
                # get vehicle path in drive
                vehicle_path = drive.solution[vehicle_id, step]
                # get all passengers in vehicle
                passengers = np.where(self.solution[:, step] == vehicle_id)[0]
                # get all paths that these passengers are on
                paths = ride_path.solution[passengers, step]
                unique_paths = [(vehicle_path[0], vehicle_path[1])]
                for path in paths:
                    if (path[0], path[1]) not in unique_paths:
                        unique_paths.append((path[0], path[1]))
                print(unique_paths)
                # check that there is only one path
                check *= len(unique_paths) <= 1
        return self._check_violation(bool(check))

    def check_constraint(self, ride_path: RidePath, drive: Drive, ride_link_constraint=True, vehicle_number_link_ride_constraint=True, vehicle_capacity_constraint=True, vehicle_only_in_one_edge_condition=True) -> bool:
        '''Constraint: All constraints

        Args:
            ride_path (RidePath): ride path object
            ride_link_constraint (bool, optional): Constraint: passenger use car only when they use the path and contrary. Defaults to True.
            vehicle_number_link_ride_constraint (bool, optional): Constraint: vehicle number is the same in ridePath and rideVehicle. Defaults to True.
            vehicle_capacity_constraint (bool, optional): Constraint: Vehicle capacity limit. Defaults to True.
            vehicle_only_in_one_edge_condition (bool, optional): Constraint: a vehicle can only be in a edge a a time at maximum. Defaults to True.
        '''
        self.violation_count = 0
        check = True
        if ride_link_constraint:
            check *= self._check_ride_link_constraint(ride_path)
        if vehicle_number_link_ride_constraint:
            check *= self._check_vehicle_number_link_ride_constraint(
                ride_path)
        if vehicle_capacity_constraint:
            check *= self._check_vehicle_capacity_constraint()
        if vehicle_only_in_one_edge_condition:
            check *= self._check_vehicle_only_in_one_edge_condition(
                ride_path, drive)
        return check

    def get_neighbor(self, rate, temperature):
        neighbor = self.copy()
        for step in range(self.nb_steps - 1):
            for entity in range(self.nb_entity):
                if np.random.rand() < rate:
                    neighbor.solution[entity, step] += temperature * \
                        np.random.choice([-1, 1])
        return neighbor
