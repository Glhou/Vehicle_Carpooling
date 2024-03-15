# vehicle_carpooling/node.py

""" Vehicle carpooling optimization package's node module
"""


class Node:
    """ Node class
    """

    def __init__(self, id, x, y, incLanes=[]):
        self.id = id
        self.x = x
        self.y = y
        self.incLanes = incLanes
        self.from_edges = []
        self.to_edges = []
        self.from_nodes = []
        self.to_nodes = []

    def add_edge(self, edge):
        """ Add an edge
        """
        if edge.from_node == self.id:
            self.from_edges.append(edge)
            self.to_nodes.append(edge.to_node)
        else:
            self.to_edges.append(edge)
            self.from_nodes.append(edge.from_node)

    def add_from_node(self, node):
        """ Add a from node
        """
        self.from_nodes.append(node)

    def add_to_node(self, node):
        """ Add a next node
        """
        self.next_nodes.append(node)
