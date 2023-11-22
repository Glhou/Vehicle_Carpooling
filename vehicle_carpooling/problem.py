# vehicle_carpooling/problem.py

'''Defines the Problem class
'''

import numpy as np


class Problem:
    """Problem Class
    """

    def __init__(self,
                 nb_nodes: int,
                 nb_vehicles: int,
                 vehicle_capacity: int,
                 nb_passengers: int,
                 nb_steps: int,
                 path_map: np.ndarray,
                 time_map: np.ndarray,
                 passenger_start_points: np.ndarray,
                 passenger_finish_points: np.ndarray,
                 vehicle_start_points: np.ndarray,
                 alpha: int) -> None:
        """Initialize the Problem object

        Args:
            nb_nodes (int): number of nodes. Defaults to 0.
            nb_vehicles (int): number of vehicles. Defaults to 0.
            vehicle_capacity (int): vehicles capacity. Defaults to 0.
            nb_passengers (int): number of passengers. Defaults to 0.
            nb_steps (int): number of maximum steps of the optimization. Defaults to 0.
            path_map (numpy.ndarray): possible path on the map. Defaults to np.array([]).
            time_map (numpy.ndarray): time to travel each path on the map. Defaults to np.array([]).
            passenger_start_points (numpy.ndarray): starting points of the passengers. Defaults to np.array([]).
            passenger_finish_points (numpy.ndarray): finishing points of the passengers. Defaults to np.array([]).
            vehicle_start_points (numpy.ndarray): starting points of the vehicles. Defaults to np.array([]).
            alpha (int): Parameter to balance the optimization between time (alpha=0) and number of vehicles (alpha=1). Defaults to 0.
        """
        self.nb_nodes = nb_nodes
        self.nb_vehicles = nb_vehicles
        self.vehicle_capacity = vehicle_capacity
        self.nb_passengers = nb_passengers
        self.nb_steps = nb_steps
        self.path_map = path_map
        self.time_map = time_map
        self.passenger_start_points = passenger_start_points
        self.passenger_finish_points = passenger_finish_points
        self.vehicle_start_points = vehicle_start_points
        self.alpha = alpha
