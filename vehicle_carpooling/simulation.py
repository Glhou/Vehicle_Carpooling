# vehicle_carpooling/simulation.py

""" Vehicle carpooling optimization package's simulation module
"""

import traci
import gzip
import xml.etree.ElementTree as ET
import vehicle_carpooling.vehicle
import vehicle_carpooling.passenger
import vehicle_carpooling.node
import vehicle_carpooling.edge


class Simulation:
    """ Simulation class
    """

    def __init__(self, nb_vehicles, nb_passengers, network_name, nb_nodes=0,  vehicle_start_nodes=[], passenger_start_nodes=[], passenger_finish_nodes=[]):
        """ Simulation constructor

        Args:
            nb_vehicles (int): number of vehicles
            nb_passengers (int): number of passengers
            nb_nodes (int): number of nodes
            path_map (dict): path map
            path_map_spreading (dict(dict)): path map coordinates of the nodes
            vehicle_start_nodes (list): vehicle start nodes
            passenger_start_nodes (list): passenger start nodes
            passenger_finish_nodes (list): passenger finish nodes
        """
        self.nb_vehicles = nb_vehicles
        self.nb_passengers = nb_passengers
        self.nb_nodes = nb_nodes
        self.network_name = network_name
        self.path_map = dict()
        self.nodes = dict()
        self.edges = dict()
        self.vehicle_start_nodes = vehicle_start_nodes
        self.passenger_start_nodes = passenger_start_nodes
        self.passenger_finish_nodes = passenger_finish_nodes
        self.vehicles = []
        self.passengers = []

    def import_sumo_nework(self):
        """ Import the sumo network
        """
        # Open the sumo network file in data/self.network_name.net.xml
        with gzip.open('data/' + self.network_name + '.net.xml.gz', 'rb') as f:
            tree = ET.parse(f)
            root = tree.getroot()

            # Get all jonction in the sumo network
            for junction in root.findall('junction'):
                type = junction.get('type')
                if type != 'internal':
                    node = vehicle_carpooling.node.Node(junction.get('id'), float(junction.get('x')), float(
                        junction.get('y')), junction.get('incLanes').split(' '))
                    if node.incLanes == ['']:
                        node.incLanes = []
                    self.nodes[node.id] = node

            # Get all road edges in the sumo network
            for edge in root.findall('edge'):
                lanes = edge.findall('lane')
                if edge.get('function') != 'internal' and lanes:
                    self.edges[edge.get('id')] = vehicle_carpooling.edge.Edge(
                        edge.get('id'), [lane.get('id') for lane in lanes], edge.get('from'), edge.get('to'), edge.get('type'))

            # for all edges, get the from node and the to node
            for _, edge in self.edges.items():
                # add to the node the edge
                from_node = self.nodes.get(edge.from_node, None)
                if from_node:
                    from_node.add_edge(edge)
                to_node = self.nodes.get(edge.to_node, None)
                if to_node:
                    to_node.add_edge(edge)

            # remove nodes with no edges
            for node_id, node in self.nodes.copy().items():
                if len(node.from_edges) == 0 and len(node.to_edges) == 0:
                    del self.nodes[node_id]

            # set nb_nodes if not set
            if self.nb_nodes == 0:
                self.nb_nodes = len(self.nodes)

            for _, node in self.nodes.items():
                for to_node in node.to_nodes:
                    self.path_map.setdefault(node.id, []).append(to_node)

    def configure_vehicles(self):
        """ Recreate the data/osm.passenger.trips.xml file and add points to points.poly.xml
        """
        # Create the trips xml
        root = ET.Element('routes')
        tree = ET.ElementTree(root)
        vType = ET.SubElement(root, 'vType')
        vType.set('id', 'veh_passenger')
        vType.set('vClass', 'passenger')
        root.clear()
        root.append(vType)

        # Create the points xml
        root_points = ET.Element('additional')
        tree_points = ET.ElementTree(root_points)
        root_points.clear()

        # for all vehicles, create the trip element
        for vehicle in self.vehicles:
            print(vehicle.path)
            try:
                trip = ET.SubElement(root, 'trip')
                trip.set('id', str(vehicle.id))
                trip.set('type', 'veh_passenger')
                trip.set('depart', '0')
                trip.set('departLane', 'best')
                trip.set('from', vehicle.path[0])
                trip.set('to', vehicle.path[-1])
                if vehicle.path[1:-1]:
                    trip.set('via', ' '.join(vehicle.path[1:-1]))
                trip.set('departSpeed', '0')

                for i, edge in enumerate(vehicle.path):
                    poi = ET.SubElement(root_points, 'poi')
                    idd = i
                    color = 'blue'
                    if idd == 0:
                        idd = 's'
                        color = 'green'
                    if idd == len(vehicle.path) - 1:
                        idd = 'f'
                        color = 'red'
                    poi.set('id', f'light{vehicle.id}_{idd}')
                    poi.set('color', color)
                    poi.set('type', 'light')
                    poi.set('layer', '10')
                    poi.set('lane', self.edges[edge].lanes_id[0])
                    poi.set('pos', '50')

            except IndexError:
                print("Vehicle " + str(vehicle.id) + " has no path")

        # write the xml file
        tree.write('data/osm.passenger.trips.xml')
        tree_points.write('data/points.poly.xml')

    def set_vehicle_start_nodes(self, vehicle_start_nodes):
        """ Set the vehicle start nodes
        """
        self.nb_vehicles = len(vehicle_start_nodes)
        self.vehicle_start_nodes = vehicle_start_nodes

    def set_passenger_start_and_finish_nodes(self, passenger_start_nodes, passenger_finish_nodes):
        """ Set the passenger start and finish nodes
        """
        self.nb_passengers = len(passenger_start_nodes)
        if len(passenger_start_nodes) != len(passenger_finish_nodes):
            raise Exception(
                "Passenger start nodes and passenger finish nodes must have the same length")
        self.passenger_start_nodes = passenger_start_nodes
        self.passenger_finish_nodes = passenger_finish_nodes

    def create_vehicles(self):
        """ Create the vehicles
        """
        for vehicle in range(self.nb_vehicles):
            self.vehicles.append(vehicle_carpooling.vehicle.Vehicle(
                self.vehicle_start_nodes[vehicle], 4))

    def create_passengers(self):
        """ Create the passengers
        """
        for passenger in range(self.nb_passengers):
            self.passengers.append(vehicle_carpooling.passenger.Passenger(
                self.passenger_start_nodes[passenger], self.passenger_finish_nodes[passenger]))

    def compute_paths(self):
        """ Compute the paths of the vehicles
        """
        for vehicle in self.vehicles:
            vehicle.compute_path_coordinates(self.nodes)
            vehicle.compute_path(self.path_map, self.nodes)

    def run(self):
        """ Run the simulation
        """
        self.configure()
        sumo_cmd = [
            "sumo", "-c", "data/carpool.sumocfg" '--save-configuration', 'data/debug.sumocfg']
        traci.start(sumo_cmd)

        while traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep()

        # Get the travel time of the vehicle
        for vehicle in self.vehicles:
            vehicle.travel_time.waiting_time = traci.vehicle.getAccumulatedWaitingTime(
                vehicle.id)
            vehicle.travel_time.travel_time += traci.vehicle.getAccumulatedTravelTime(
                vehicle.id)

        traci.close()
