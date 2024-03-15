# vehicle_carpooling/passenger.py

""" Vehicle carpooling optimization package's passenger module
"""


class Passenger:
    """ Passenger class
    """

    def __init__(self, start_node, finish_node):
        self.id = id(self)
        self.start_node = start_node
        self.finish_node = finish_node
        self.vehicle = None

    def add_vehicle(self, vehicle):
        """ Add a vehicle to the passenger
        """
        self.vehicle = vehicle
