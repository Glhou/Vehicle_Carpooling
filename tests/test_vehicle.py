# tests/test_vehicle.py

""" vehicle module tests
"""

import unittest
from vehicle_carpooling.vehicle import Vehicle
from vehicle_carpooling.passenger import Passenger
from vehicle_carpooling.node import Node
from vehicle_carpooling.edge import Edge


class TestComputePath(unittest.TestCase):
    def setUp(self):
        """
        A - B
        |   |
        C - D
        """
        self.path_map = {
            'A': ['B', 'C'],
            'B': ['A', 'D'],
            'C': ['A', 'D'],
            'D': ['B', 'C']
        }
        self.nodes = {
            'A': Node('A', 0, 0, ['A_B', 'A_C']),
            'B': Node('B', 0, 1, ['B_A', 'B_D']),
            'C': Node('C', 1, 0, ['C_A', 'C_D']),
            'D': Node('D', 1, 1, ['D_B', 'D_C'])
        }

        self.edges = {
            'A_B': Edge('A_B', 'A_B', 'A', 'B'),
            'B_A': Edge('B_A', 'B_A', 'B', 'A'),
            'A_C': Edge('A_C', 'A_C', 'A', 'C'),
            'C_A': Edge('C_A', 'C_A', 'C', 'A'),
            'B_D': Edge('B_D', 'B_D', 'B', 'D'),
            'D_B': Edge('D_B', 'D_B', 'D', 'B'),
            'C_D': Edge('C_D', 'C_D', 'C', 'D'),
            'D_C': Edge('D_C', 'D_C', 'D', 'C')
        }

        self.nodes['A'].add_edge(self.edges['A_B'])
        self.nodes['A'].add_edge(self.edges['A_C'])
        self.nodes['A'].add_edge(self.edges['B_A'])
        self.nodes['A'].add_edge(self.edges['C_A'])
        self.nodes['B'].add_edge(self.edges['B_A'])
        self.nodes['B'].add_edge(self.edges['B_D'])
        self.nodes['B'].add_edge(self.edges['A_B'])
        self.nodes['B'].add_edge(self.edges['D_B'])
        self.nodes['C'].add_edge(self.edges['C_A'])
        self.nodes['C'].add_edge(self.edges['C_D'])
        self.nodes['C'].add_edge(self.edges['A_C'])
        self.nodes['C'].add_edge(self.edges['D_C'])
        self.nodes['D'].add_edge(self.edges['D_B'])
        self.nodes['D'].add_edge(self.edges['D_C'])
        self.nodes['D'].add_edge(self.edges['B_D'])
        self.nodes['D'].add_edge(self.edges['C_D'])

        self.passenger1 = Passenger('A', 'B')
        self.passenger2 = Passenger('B', 'C')
        self.vehicle = Vehicle('A', 4)
        self.vehicle.add_passenger(self.passenger1)
        self.vehicle.add_passenger(self.passenger2)

    def test_compute_path_with_nodes(self):
        self.vehicle.compute_path_nodes(self.path_map)
        self.vehicle.compute_path(self.path_map, self.nodes)
        self.assertEqual(self.vehicle.path_nodes, ['A', 'B', 'C'])
        self.assertTrue(self.vehicle.path == [
                        'A_B', 'B_A', 'A_C'] or self.vehicle.path == ['A_B', "B_D", "D_C"])

    def test_compute_path_no_passengers_with_nodes(self):
        self.vehicle.passengers = []
        self.vehicle.compute_path_nodes(self.path_map)
        self.vehicle.compute_path(self.path_map, self.nodes)
        self.assertEqual(self.vehicle.path, [])

    def test_compute_path_no_passengers_with_coordinates(self):
        self.vehicle.passengers = []
        self.vehicle.compute_path_coordinates(self.nodes)
        self.vehicle.compute_path(self.path_map, self.nodes)
        self.assertEqual(self.vehicle.path, [])

    def test_compute_path_with_coordinates(self):
        self.vehicle.path_nodes = []
        self.vehicle.compute_path_coordinates(self.nodes)
        self.vehicle.compute_path(self.path_map, self.nodes)
        self.assertEqual(self.vehicle.path_nodes, ['A', 'B', 'C'])
        self.assertTrue(self.vehicle.path == [
                        'A_B', 'B_A', 'A_C'] or self.vehicle.path == ['A_B', "B_D", "D_C"])

    def test_compute_path_coordinates(self):
        nodes = {
            'A': Node('A', 0, 0),
            'B': Node('B', 1, 1),
            'C': Node('C', 2, 2),
            'D': Node('D', 3, 3)
        }
        passengers = [
            Passenger('B', 'C'),
            Passenger('D', 'A')
        ]
        vehicle = Vehicle('A', 2)
        vehicle.passengers = passengers
        expected_path = ['A', 'B', 'C', 'D', 'A']
        vehicle.compute_path_coordinates(nodes)
        self.assertEqual(
            vehicle.path_nodes, expected_path)
