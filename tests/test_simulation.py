# tests/test_simulation.py

""" solution module tests
"""

import unittest
from unittest.mock import patch, mock_open, Mock
import os
import xml.etree.ElementTree as ET
from vehicle_carpooling.simulation import Simulation
from xml.etree.ElementTree import Element


class TestSimulation(unittest.TestCase):
    def setUp(self):
        nb_vehicles = 1
        nb_passengers = 1
        self.simulation = Simulation(
            nb_vehicles, nb_passengers, 'osm')

    @patch('gzip.open')
    @patch('xml.etree.ElementTree.parse')
    def test_import_sumo_network(self, mock_parse, mock_open):
        # Mock the XML tree returned by ET.parse
        mock_tree = mock_parse.return_value
        mock_root = mock_tree.getroot.return_value

        # Mock the lane elements in the XML tree
        mock_lanes = [Mock(), Mock(), Mock(), Mock()]
        mock_lanes[0].get.side_effect = lambda attr, default=None: {
            'id': 'lane1'}.get(attr, default)
        mock_lanes[1].get.side_effect = lambda attr, default=None: {
            'id': 'lane2'}.get(attr, default)
        mock_lanes[2].get.side_effect = lambda attr, default=None: {
            'id': 'lane3'}.get(attr, default)
        mock_lanes[3].get.side_effect = lambda attr, default=None: {
            'id': 'lane4'}.get(attr, default)

        # Mock the junction elements in the XML tree
        mock_junctions = [Mock(), Mock(), Mock()]
        mock_junctions[0].get.side_effect = lambda attr: {
            'id': 'id1', 'x': 10.0, 'y': 20.0, 'incLanes': ' '.join([mock_lanes[0].get('id'), mock_lanes[1].get('id')]), 'intLanes': '', 'type': ''}[attr]
        mock_junctions[1].get.side_effect = lambda attr: {
            'id': 'id2', 'x': 30.0, 'y': 40.0, 'incLanes': ' '.join([mock_lanes[2].get('id')]), 'intLanes': '', 'type': ''}[attr]
        mock_junctions[2].get.side_effect = lambda attr: {
            'id': 'id3', 'x': 20.0, 'y': 40.0, 'incLanes': ''.join([mock_lanes[3].get('id')]), 'intLanes': '', 'type': ''}[attr]

        # Mock the edge elements in the XML tree
        mock_edges = [Mock(spec=Element), Mock(spec=Element),
                      Mock(spec=Element), Mock(spec=Element)]
        mock_edges[0].get.side_effect = lambda attr, default = None: {
            'id': 'edge1', 'from': mock_junctions[1].get('id'), 'to': mock_junctions[0].get('id'), "type": "highway.residential"}.get(attr, default)
        mock_edges[0].findall.return_value = [mock_lanes[0]]
        mock_edges[1].get.side_effect = lambda attr, default= None: {
            'id': 'edge2', 'from': mock_junctions[2].get('id'), 'to': mock_junctions[0].get('id'), "type": "highway.residential"}.get(attr, default)
        mock_edges[1].findall.return_value = [mock_lanes[1]]
        mock_edges[2].get.side_effect = lambda attr, default = None: {
            'id': '-edge1', 'from': mock_junctions[0].get('id'), 'to': mock_junctions[1].get('id'), "type": "highway.residential"}.get(attr, default)
        mock_edges[2].findall.return_value = [mock_lanes[2]]
        mock_edges[3].get.side_effect = lambda attr, default= None: {
            'id': '-edge2', 'from': mock_junctions[0].get('id'), 'to': mock_junctions[2].get('id'), "type": "highway.residential"}.get(attr, default)
        mock_edges[3].findall.return_value = [mock_lanes[3]]

        mock_root.findall.side_effect = lambda attr: {
            'junction': mock_junctions, 'edge': mock_edges}[attr]

        # Call the function
        self.simulation.import_sumo_nework()

        # Check if the nodes were imported correctly
        self.assertEqual(len(self.simulation.nodes), 3)
        self.assertEqual(self.simulation.nodes['id1'].id, 'id1')
        self.assertEqual(self.simulation.nodes['id1'].x, 10)
        self.assertEqual(self.simulation.nodes['id1'].y, 20)
        self.assertEqual(self.simulation.nodes['id1'].incLanes, [
                         'lane1', 'lane2'])
        self.assertEqual([edge.id for edge in self.simulation.nodes['id1'].from_edges], [
                         '-edge1', '-edge2'])
        self.assertEqual([edge.id for edge in self.simulation.nodes['id1'].to_edges], [
                         'edge1', 'edge2'])
        self.assertEqual(
            self.simulation.nodes['id1'].from_nodes, ['id2', 'id3'])
        self.assertEqual(self.simulation.nodes['id1'].to_nodes, ['id2', 'id3'])

        # Check if the path_map was populated correctly
        self.assertEqual(self.simulation.path_map, {
                         'id1': ['id2', 'id3'], 'id2': ['id1'], 'id3': ['id1']})

    def test_integration_import_sumo_network(self):
        self.simulation.import_sumo_nework()
        self.assertIsNotNone(self.simulation.nodes)

    def test_integration_configure_vehicles(self):
        # Import the sumo network
        print('Import started')
        self.simulation.import_sumo_nework()
        print('Import ended')
        # Create vehicles start nodes, passengers start nodes and passengers finish nodes
        test_nb_vehicles = 1
        test_nb_passengers = 4
        vehicle_start_nodes = []
        passenger_start_nodes = []
        passenger_finish_nodes = []
        for i in range(test_nb_vehicles):
            vehicle_start_nodes.append(
                list(self.simulation.nodes.items())[i][1].id)
        for i in range(test_nb_passengers):
            passenger_start_nodes.append(
                list(self.simulation.nodes.items())[i + test_nb_vehicles][1].id)
            passenger_finish_nodes.append(
                list(self.simulation.nodes.items())[i + test_nb_vehicles + test_nb_passengers][1].id)

        self.simulation.set_vehicle_start_nodes(vehicle_start_nodes)
        self.simulation.set_passenger_start_and_finish_nodes(
            passenger_start_nodes, passenger_finish_nodes)

        # Create vehicles and passengers
        self.simulation.create_vehicles()
        self.simulation.create_passengers()
        # add passengers to vehicles
        for i in range(test_nb_passengers):
            self.simulation.vehicles[0].add_passenger(
                self.simulation.passengers[i])
        print(f'Vehicle start node: {self.simulation.vehicles[0].start_node}')
        print(
            f'Passenger start node: {self.simulation.passengers[0].start_node}')
        print(
            f'Passenger finish node: {self.simulation.passengers[0].finish_node}')
        # Compute the path of the vehicles
        print('Compute paths started')
        self.simulation.compute_paths()
        print('Compute paths ended')

        # Call the function
        print('Configure vehicles started')
        self.simulation.configure_vehicles()
        print('Configure vehicles ended')

        # Check if the file is created
        self.assertTrue(os.path.exists('data/osm.passenger.trips.xml'))


if __name__ == '__main__':
    unittest.main()
