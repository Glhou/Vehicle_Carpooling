# vehicle_carpooling/solution.py

"""Defines the Solution, Ride and Drive class
"""

import numpy as np


class Solution:
    """Solution class
    """

    def __init__(self, nb_steps, nb_nodes, nb_entity) -> None:
        """Initialize the Solution object

        Args:
            nb_steps (int): number of maximum steps
            nb_nodes (int): number of nodes
            nb_entity (int): number of entity (passenger / vehicles)
        """
        self.nb_steps = nb_steps
        self.nb_nodes = nb_nodes
        self.nb_entity = nb_entity
        self.solution = np.zeros((nb_steps, nb_nodes, nb_nodes, nb_entity))

    def _iter(self, depth):
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
            self.solution[step] = np.clip(self.solution[step], 0, 1)
        else:
            self.solution = np.clip(self.solution, 0, 1)

    def _shuffle_step(self, step: int, rate: int, path_map: np.ndarray):
        """Shuffle a step of the solution

        Args:
            step (int): step to shuffle
            rate (int): rate of the shuffle (0 to 1)
            path_map (np.array): possible path on the map
        """
        for node_k, node_l in zip(range(self.nb_nodes), range(self.nb_nodes)):
            if path_map[node_k, node_l]:
                random_matrix = np.random.choice([-1, 1], self.nb_entity)
                self.solution[step, node_k, node_l] += rate * random_matrix
        self._clip(step)

    def shuffle(self, rate: int, path_map: np.ndarray) -> None:
        """Shuffle the solution

        Args:
            rate (float): rate of the shuffle (0 to 1)
            path_map (np.array): possible path on the map
        """
        for _, passenger_map in enumerate(self.solution):
            for node_k, node_l in zip(range(self.nb_nodes), range(self.nb_nodes)):
                if path_map[node_k, node_l]:
                    random_matrix = np.random.choice([-1, 1], self.nb_entity)
                    passenger_map[node_k, node_l] += rate * random_matrix
        np.clip(self.solution, 0, 1)  # clip value between 0 and 1


class Ride(Solution):
    """Ride class
    """

    def __init__(self, nb_steps, nb_nodes, nb_passengers) -> None:
        """Initialize the Ride object

        Args:
            nb_steps (int): number of maximum steps
            nb_nodes (int): number of nodes
            nb_passengers (int): number of passengers
            passenger_start_points (np.ndarray): passenger start points
            passenger_finish_points (np.ndarray): passenger finish points
            path_map (np.ndarray): possible path on the map
        """
        super().__init__(nb_steps, nb_nodes, nb_passengers)
        self.passenger_start_points = passenger_start_points
        self.passenger_finish_points = passenger_finish_points
        self.path_map = path_map
        self.nb_vehicle = nb_vehicle
        self.vehicle_capacity = vehicle_capacity

    def _check_start_finish_constraint(self):
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

    def _check_path_constraint(self):
        '''Constraint: Passengers cannot be on non paths (use R and M)
        '''
        check = True
        for step, k, l in self._iter(3):
            if self.path_map[k][l] == 0:
                check *= sum(self.solution[step, k, l, :]) == 0
        return check

    def _check_continuous_constraint(self):
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

    def _check_action_per_step_constraint(self):
        '''Constraint: Passengers can only use one path per step
        '''
        check = True
        for passenger in range(self.nb_entity):
            for step in range(self.nb_steps):
                # you stay on the same point or you move
                check *= sum(sum(self.solution[step, :, :, passenger])) == 1
        return check

    def _check_limit_vehicle_constraint(self):
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
            check *= nb_used_vehicles <= self.nb_vehicle
        return bool(check)

    def check_constraint(self, start_finish_constraint=True, path_constraint=True, continuous_constraint=True, action_per_step_constraint=True, limit_vehicle_constraint=True):
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


class Drive(Solution):
    """Drive class
    """

    def __init__(self, nb_steps, nb_nodes, nb_vehicles) -> None:
        """Initialize the Drive object

        Args:
            nb_steps (int): number of maximum steps
            nb_nodes (int): number of nodes
            nb_vehicles (int): number of vehicles
        """
        super().__init__(nb_steps, nb_nodes, nb_vehicles)
