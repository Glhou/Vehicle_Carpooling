# vehicle_carpooling/solution.py

"""Defines the Solution, Ride and Drive class
"""

import numpy as np
import math


class Solution:
    """Solution class
    """

    def __init__(self, nb_steps, nb_nodes, nb_entity, path_map) -> None:
        """Initialize the Solution object

        Args:
            nb_steps (int): number of maximum steps
            nb_nodes (int): number of nodes
            nb_entity (int): number of entity (passenger / vehicles)
            path_map (np.ndarray): possible path on the map
        """
        self.nb_steps = nb_steps
        self.nb_nodes = nb_nodes
        self.nb_entity = nb_entity
        self.path_map = path_map
        self.discrete_solution = np.zeros(
            (nb_steps, nb_nodes, nb_nodes, nb_entity))
        self.solution = np.zeros((nb_steps, nb_nodes, nb_nodes, nb_entity))

    def _iter(self, depth=4):
        """Return iterator of indexes the solution using the solution shape

        Args:
            depth (int): depth of the iterator (ex: 1 return an iterator on step only)
        """
        if depth == 1:
            return [i[0] for i in np.ndindex(self.solution.shape[0])]
        return np.ndindex(self.solution.shape[:depth])

    def _clip(self, step=None):
        """Clip the solution to 0 1 values
        """
        if step:
            self.discrete_solution[step] = np.clip(
                self.discrete_solution[step], 0, 1)
            self.solution[step] = np.clip(self.solution[step], 0, 1)
        else:
            self.solution = np.clip(self.solution, 0, 1)
            self.discrete_solution = np.clip(self.discrete_solution, 0, 1)

    def _shuffle_step(self, step: int, rate: int, path_map: np.ndarray):
        """Shuffle a step of the solution

        Args:
            step (int): step to shuffle
            rate (int): rate of the shuffle (0 to 1)
            path_map (np.array): possible path on the map
        """
        for node_k in range(self.nb_nodes):
            for node_l in range(self.nb_nodes):
                if path_map[node_k, node_l]:
                    random_matrix = np.random.choice([-1, 1], self.nb_entity)
                    self.discrete_solution[step, node_k,
                                           node_l] += rate * random_matrix
        self._update_solution()
        self._clip(step)

    def shuffle(self, rate: int, path_map: np.ndarray) -> None:
        """Shuffle the solution

        Args:
            rate (float): rate of the shuffle (0 to 1)
            path_map (np.array): possible path on the map
        """
        for step, _ in enumerate(self.solution):
            self._shuffle_step(step, rate, path_map)

    def _update_solution(self):
        """Update the solution
        """
        for step, node_k, node_l, entity in self._iter():
            if self.solution[step, node_k, node_l, entity] >= 0.5:
                self.discrete_solution[step, node_k, node_l, entity] = 1
            else:
                self.discrete_solution[step, node_k, node_l, entity] = 0


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
        super().__init__(nb_steps, nb_nodes, nb_passengers, path_map)
        self.passenger_start_points = passenger_start_points
        self.passenger_finish_points = passenger_finish_points
        self.nb_vehicles = nb_vehicles
        self.vehicle_capacity = vehicle_capacity

    def _check_start_finish_constraint(self) -> bool:
        '''Constraint: Each passenger must start and finish in designated places
        '''
        check = True
        for passenger in range(self.nb_entity):
            check *= sum(self.solution[0,
                         self.passenger_start_points[passenger], :, passenger]) == 1
            # passenger finish at PF[i]
            check *= sum(self.solution[-1, :,
                         self.passenger_finish_points[passenger], passenger]) == 1
            # when you arrives you don't move
            for l in range(self.nb_nodes):
                if l != self.passenger_finish_points[passenger]:
                    check *= sum(
                        self.solution[:, self.passenger_finish_points[passenger], l, passenger]) == 0
        return check

    def _check_path_constraint(self) -> bool:
        '''Constraint: Passengers cannot be on non paths (use R and M)
        '''
        check = True
        for step, k, l in self._iter(3):
            if self.path_map[k][l] == 0:
                check *= sum(self.solution[step, k, l, :]) == 0
        return check

    def _check_continuous_constraint(self) -> bool:
        '''Constraint: The path needs to be continuous
        '''
        check = True
        for passenger in range(self.nb_entity):
            for node in range(self.nb_nodes):
                if node != self.passenger_finish_points[passenger]:
                    for step in range(self.nb_steps-1):
                        check *= sum(self.solution[step, :, node, passenger]) == sum(
                            self.solution[step+1, node, :, passenger])
        return check

    def _check_action_per_step_constraint(self) -> bool:
        '''Constraint: Passengers can only use one path per step
        '''
        check = True
        for passenger in range(self.nb_entity):
            for step in range(self.nb_steps):
                # you stay on the same point or you move
                check *= sum(sum(self.solution[step, :, :, passenger])) == 1
        return check

    def _check_limit_vehicle_constraint(self) -> bool:
        '''Constraint: There is a limited total number of vehicles at each step
        '''
        check = True
        for step, k, l in self._iter(3):
            nb_used_vehicles = 0
            if k != l:
                if self.path_map[k, l]:
                    nb_used_vehicles_on_edge = math.ceil(
                        sum(self.solution[step, k, l, :])/self.vehicle_capacity)
                    nb_used_vehicles += nb_used_vehicles_on_edge
            check *= nb_used_vehicles <= self.nb_vehicles
        return bool(check)

    def check_constraint(self, start_finish_constraint=True, path_constraint=True, continuous_constraint=True, action_per_step_constraint=True, limit_vehicle_constraint=True) -> bool:
        '''Constraint: All constraints

        Args:
            start_finish_constraint (bool, optional): Constraint: Each passenger must start and finish in designated places. Defaults to True.
            path_constraint (bool, optional): Constraint: Passengers cannot be on non paths (use R and M). Defaults to True.
            continuous_constraint (bool, optional): Constraint: The path needs to be continuous. Defaults to True.
            action_per_step_constraint (bool, optional): Constraint: Passengers can only use one path per step. Defaults to True.
            limit_vehicle_constraint (bool, optional): Constraint: There is a limited total number of vehicles at each step. Defaults to True.
        '''
        check = True
        if start_finish_constraint:
            check *= self._check_start_finish_constraint()
        if path_constraint:
            check *= self._check_path_constraint()
        if continuous_constraint:
            check *= self._check_continuous_constraint()
        if action_per_step_constraint:
            check *= self._check_action_per_step_constraint()
        if limit_vehicle_constraint:
            check *= self._check_limit_vehicle_constraint()
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
        super().__init__(nb_steps, nb_nodes, nb_passengers, path_map)
        self.nb_vehicles = nb_vehicles
        self.vehicle_capacity = vehicle_capacity

    def _check_ride_link_constraint(self, ride_path: RidePath) -> bool:
        '''Constraint: passenger use car only when they use the path and contrary
        '''
        check = True
        for step, k, l, passenger in self._iter():
            if k != l:
                if ride_path.solution[step, k, l, passenger] == 1:
                    check *= self.solution[step, k, l,
                                           passenger] >= 0
                else:
                    check *= self.solution[step, k, l, passenger] == -1
        return check

    def _check_vehicle_number_link_ride_constraint(self, ride_path: RidePath) -> bool:
        '''Constraint: vehicle number is the same in ridePath and rideVehicle
        '''
        check = True
        for step, k, l in self._iter(3):
            if k != l:
                without_none = np.delete(self.solution[step, k, l], np.where(
                    self.solution[step, k, l] == -1))
                nb_vehicle_self = len(
                    np.unique(without_none))
                nb_vehicle_ride_path = math.ceil(
                    sum(ride_path.solution[step, k, l, :])/self.vehicle_capacity)
                print((step, k, l), nb_vehicle_ride_path, nb_vehicle_self,
                      np.unique(np.delete(self.solution[step, k, l], np.where(self.solution[step, k, l] == -1))))
                check *= nb_vehicle_self == nb_vehicle_ride_path
        return check

    def _check_vehicle_capacity_constraint(self) -> bool:
        '''Constraint: Vehicle capacity limit
        '''
        check = True
        for step, k, l in self._iter(3):
            if k != l:
                if self.path_map[k, l]:
                    nb_passenger_in_vehicle = 0
                    for vehicle_id in range(self.nb_vehicles):
                        nb_passenger_in_vehicle = np.count_nonzero(
                            self.solution[step, k, l] == vehicle_id)
                        check *= nb_passenger_in_vehicle <= self.vehicle_capacity
        return bool(check)

    def _check_vehicle_only_in_one_edge_condition(self) -> bool:
        """Constraint: a vehicle can only be in a edge a a time at maximum
        """
        check = True
        for step in range(self.nb_steps):
            for vehicle_id in range(self.nb_vehicles):
                nb_occurence_in_edges = 0
                for k in range(self.nb_nodes):
                    for l in range(self.nb_nodes):
                        if k != l:
                            if self.path_map[k, l]:
                                if vehicle_id in self.solution[step, k, l]:
                                    nb_occurence_in_edges += 1
                check *= nb_occurence_in_edges <= 1
        return bool(check)

    def check_constraint(self, ride_path: RidePath, ride_link_constraint=True, vehicle_number_link_ride_constraint=True, vehicle_capacity_constraint=True, vehicle_only_in_one_edge_condition=True) -> bool:
        '''Constraint: All constraints

        Args:
            ride_path (RidePath): ride path object
            ride_link_constraint (bool, optional): Constraint: passenger use car only when they use the path and contrary. Defaults to True.
            vehicle_number_link_ride_constraint (bool, optional): Constraint: vehicle number is the same in ridePath and rideVehicle. Defaults to True.
            vehicle_capacity_constraint (bool, optional): Constraint: Vehicle capacity limit. Defaults to True.
            vehicle_only_in_one_edge_condition (bool, optional): Constraint: a vehicle can only be in a edge a a time at maximum. Defaults to True.
        '''
        check = True
        if ride_link_constraint:
            check *= self._check_ride_link_constraint(ride_path)
        if vehicle_number_link_ride_constraint:
            check *= self._check_vehicle_number_link_ride_constraint(
                ride_path)
        if vehicle_capacity_constraint:
            check *= self._check_vehicle_capacity_constraint()
        if vehicle_only_in_one_edge_condition:
            check *= self._check_vehicle_only_in_one_edge_condition()
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
        super().__init__(nb_steps, nb_nodes, nb_vehicles, path_map)
        self.vehicle_capacity = vehicle_capacity
        self.vehicle_start_points = vehicle_start_points

    def _check_vehicle_start_constraint(self) -> bool:
        '''Constraint: Each vehicle must start at designated places
        '''
        check = True
        for vehicle in range(self.nb_entity):
            check *= sum(self.solution[0,
                         self.vehicle_start_points[vehicle], :, vehicle]) == 1
        return check

    def _check_vehicles_path_constraint(self) -> bool:
        '''Constraint: Vehicle cannot be on non paths
        '''
        check = True
        for step, k, l in self._iter(3):
            if self.path_map[k][l] == 0:
                check *= sum(self.solution[step, k, l, :]) == 0
        return check

    def _check_vehicles_continuous_constraint(self) -> bool:
        '''Constraint: The path needs to be continuous
        '''
        check = True
        for vehicle in range(self.nb_entity):
            for node in range(self.nb_nodes):
                for step in range(self.nb_steps-1):
                    check *= sum(self.solution[step, :, node, vehicle]) == sum(
                        self.solution[step+1, node, :, vehicle])
        return check

    def _check_vehicle_action_per_step_constraint(self) -> bool:
        '''Constraint: Vehicle can only use one path per step
        '''
        check = True
        for vehicle in range(self.nb_entity):
            for step in range(self.nb_steps):
                check *= sum(sum(self.solution[step, :, :, vehicle])) == 1
        return check

    def check_constraint(self, vehicle_start_constraint=True, vehicles_path_constraint=True, vehicles_continuous_constraint=True, vehicle_action_per_step_constraint=True) -> bool:
        '''Constraint: All constraints

        Args:
            limit_vehicle_constraint (bool, optional): Constraint: There is a limited total number of vehicles at each step. Defaults to True.
            vehicle_start_constraint (bool, optional): Constraint: Each vehicle must start at designated places. Defaults to True.
            vehicles_path_constraint (bool, optional): Constraint: Vehicle cannot be on non paths. Defaults to True.
            vehicles_continuous_constraint (bool, optional): Constraint: The path needs to be continuous. Defaults to True.
            vehicle_action_per_step_constraint (bool, optional): Constraint: Vehicle can only use one path per step. Defaults to True.
        '''
        check = True
        if vehicle_start_constraint:
            check *= self._check_vehicle_start_constraint()
        if vehicles_path_constraint:
            check *= self._check_vehicles_path_constraint()
        if vehicles_continuous_constraint:
            check *= self._check_vehicles_continuous_constraint()
        if vehicle_action_per_step_constraint:
            check *= self._check_vehicle_action_per_step_constraint()
        return check
