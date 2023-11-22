# Vehicle Carpooling Optimization

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

>This is a research project for my master thesis in Keio University.
This project is about an optimizaiton of taxi's path on a city map where users can share the same taxi.

## Getting Started

Create a `vehicle_carpooling.problem.Problem` object :
    
```python
from vehicle_carpooling.problem import Problem
problem = Problem(nb_nodes,
                 nb_vehicles,
                 vehicle_capacity,
                 nb_passengers,
                 nb_steps,
                 path_map,
                 time_map,
                 passenger_start_points,
                 passenger_finish_points,
                 vehicle_start_points,
                 alpha)
```

>Args:
    >- nb_nodes (int): number of nodes. Defaults to 0.
    >- nb_vehicles (int): number of vehicles. Defaults to 0.
    >- vehicle_capacity (int): vehicles capacity. Defaults to 0.
    >- nb_passengers (int): number of passengers. Defaults to 0.
    >- nb_steps (int): number of maximum steps of the optimization. Defaults to 0.
    >- path_map (numpy.ndarray): possible path on the map. Defaults to np.array([]).
    >- time_map (numpy.ndarray): time to travel each path on the map. Defaults to np.array([]).
    >- passenger_start_points (numpy.ndarray): starting points of the passengers. Defaults to np.array([]).
    >- passenger_finish_points (numpy.ndarray): finishing points of the passengers. Defaults to np.array([]).
    >- vehicle_start_points (numpy.ndarray): starting points of the vehicles. Defaults to np.array([]).
    >- alpha (int): Parameter to balance the optimization between time (alpha=0) and number of vehicles (alpha=1). Defaults to 0.

        

## Todo

- [x] Shuffle
- [ ] Score
- [ ] Gradient
- [ ] Conditions