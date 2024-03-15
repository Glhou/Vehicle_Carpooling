# vehicle_carpooling/path.py

""" Vehicle carpooling optimization package's path module
"""

from collections import deque


def get_direct_paths(node1, node2, path_map):
    """ Get direct paths between two nodes
    """
    paths = []
    nb_nodes = len(path_map)
    level_found = nb_nodes - 1  # maximum
    queue = deque([(node1, [node1])])
    while queue:
        node, path = queue.popleft()
        if node == node2 and len(path) <= level_found:
            paths.append(path)
            level_found = len(path)
        elif len(path) <= level_found:
            for next_node in path_map.get(node, []):
                if next_node not in path:
                    queue.append((next_node, path + [next_node]))
    return paths


def get_closest_node(queue, current_node):
    """ Get closest node
    """
    closest_node = queue[0]

    closest_distance = ((current_node.x - closest_node.x)**2 +
                        (current_node.y - closest_node.y)**2)**(1/2)
    for node in queue:
        distance = ((current_node.x - node.x)**2 +
                    (current_node.y - node.y)**2)**(1/2)
        if distance < closest_distance:
            closest_node = node
            closest_distance = distance
    return closest_node
