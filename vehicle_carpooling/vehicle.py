# vehicle_carpooling/vehicle.py

""" Vehicle carpooling optimization package's vehicle module
"""

import vehicle_carpooling.path as vc_path
import vehicle_carpooling.passenger as passenger
from dataclasses import dataclass


@dataclass
class TravelTime():
    """ TravelTime class
    """

    waiting_time: float = 0
    travel_time: float = 0


class Vehicle:
    """ Vehicle class
    """

    def __init__(self, start_node, capacity):
        self.id = id(self)
        self.start_node = start_node
        self.capacity = capacity
        self.passengers = []
        self.path_nodes = []
        self.travel_time = TravelTime()

    def add_passenger(self, passenger: passenger.Passenger):
        """ Add a passenger to the vehicle
        """
        if len(self.passengers) < self.capacity:
            self.passengers.append(passenger)
        else:
            raise Exception("Vehicle is full")

    def compute_path_nodes(self, path_map):
        """ Compute the path nodes of the vehicle according to passengers
        """
        if len(self.passengers) == 0:
            return []
        path = [self.start_node, self.passengers[0].start_node]
        if self.start_node == self.passengers[0].start_node:
            path = [self.start_node]
        done = [self.passengers[0]]
        stack = [self.passengers[0].finish_node]
        node = path[-1]
        while stack:
            next_node = stack.pop()
            direct_paths = vc_path.get_direct_paths(node, next_node, path_map)
            for passenger in self.passengers:
                for direct_path in direct_paths:
                    if passenger not in done and passenger.start_node in direct_path:
                        if passenger.start_node != node:
                            path.append(passenger.start_node)
                        done.append(passenger)
                        stack.append(passenger.finish_node)
                        direct_paths = vc_path.get_direct_paths(
                            node, passenger.finish_node, path_map)
            if not stack and len(done) != len(self.passengers):
                for passenger in self.passengers:
                    if passenger not in done:
                        if passenger.start_node != node:
                            path.append(passenger.start_node)
                        done.append(passenger)
                        stack.append(passenger.finish_node)
                        direct_paths = vc_path.get_direct_paths(
                            node, passenger.finish_node, path_map)
                        break
            node = next_node
        if node != path[-1]:
            path.append(node)
        self.path_nodes = path

    def compute_path(self, path_map, nodes):
        """ Compute the path of the vehicle according to passengers
        """
        path = []
        for i, node_id in enumerate(self.path_nodes):
            node_ob = nodes[node_id]
            # choose an edge of node_ob
            try:
                edge = node_ob.from_edges[0]
                if i == len(self.path_nodes) - 1:
                    edge = node_ob.to_edges[0]
                path.append(edge.id)
            except IndexError:
                print("Node " + str(node_ob.id) + " has no edge")
                print(f"Node's from edges: {node_ob.from_edges}")
                print(f"Node's to edges: {node_ob.to_edges}")
        self.path = path

    def compute_path_coordinates(self, nodes):
        """ Compute the path coordinates of the vehicle
        """
        if self.passengers == []:
            self.path_nodes = []
            return
        path_nodes = [self.start_node]
        current_node = nodes[self.start_node]
        queue = [nodes[p.start_node] for p in self.passengers]
        # remove current_node from queue if exisits
        if current_node in queue:
            queue.remove(current_node)
        while queue:
            # get the node in queue that is the closest to current_pos
            closest_node = vc_path.get_closest_node(queue, current_node)
            # remove closest_node from queue
            queue.remove(closest_node)
            # add closest_node to path_coordinates
            path_nodes.append(closest_node.id)
            # if closest_node is a passenger's start node add its finish node to queue
            for passenger in self.passengers:
                if closest_node.id == passenger.start_node:
                    if nodes[passenger.finish_node] not in queue:
                        queue.append(nodes[passenger.finish_node])
            current_node = closest_node
        self.path_nodes = path_nodes
