# vehicle_carpooling/edge.py

""" Vehicle carpooling optimization package's edge module
"""


class Edge:
    """ Edge class
    """

    def __init__(self, id, lanes_id, from_node, to_node, type=None, priority=None):
        self.id = id
        self.lanes_id = lanes_id
        self.from_node = from_node
        self.to_node = to_node
        self.type = type
        self.priority = priority
