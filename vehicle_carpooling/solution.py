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
        """
        super().__init__(nb_steps, nb_nodes, nb_passengers)


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
