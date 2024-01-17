# vehicle_carpooling/utils/trees.py

"""Utils for trees
"""

import numpy as np
import copy
import random


def compute_solutions(start_point, finish_point, nb_steps, next_nodes: dict):
    """Compute all the solutions of a passenger
    """
    trips = compute_trips(start_point, finish_point, nb_steps, next_nodes)
    solutions = []
    for trip in trips:
        solution = []
        for i in range(1, len(trip)):
            solution.append([trip[i-1], trip[i]])
        solutions.append(solution)
        for i in range(len(trip), nb_steps+1):
            solution.append([trip[-1], trip[-1]])
    return solutions


def compute_trips(start_point, finish_point, nb_steps, next_nodes: dict):
    """Compute the list of trips of a passenger
    """
    tree = compute_tree_trips(start_point, finish_point, nb_steps, next_nodes)
    return get_all_solutions_from_tree(tree)


def compute_tree_trips(start_point, finish_point, nb_steps, next_nodes: dict):
    """Compute the tree of trips of a passenger
    """

    def rec_compute_trips(node, finish_point, nb_steps, next_nodes: dict):
        """Compute the trips of a passenger (node = starting_point)
        """
        if node == finish_point:
            return [finish_point]
        if nb_steps == 0:
            return [node, None]
        tree = []
        for next_node in next_nodes[node]:
            next_tree = rec_compute_trips(
                next_node, finish_point, nb_steps-1, next_nodes)
            if len(next_tree) > 0:
                if next_tree[0] == finish_point:
                    tree.append(next_tree)
            if len(next_tree) > 1:  # if there is branches
                if next_tree[1]:
                    tree.append(next_tree)
        return [node, *tree]
    trips = rec_compute_trips(
        start_point, finish_point, nb_steps, next_nodes)
    if len(trips) == 1:
        return []
    return trips


def _get_node_from_tree(tree, tree_path, level):
    """Get node used in tree_path at level
    """
    next_tree = copy.deepcopy(tree)
    for i in range(level):
        next_tree = next_tree[tree_path[i]]
    return next_tree[0]


def get_solution_from_tree(tree, tree_path):
    """Return solution using tree_path
    """
    solution = []
    current_node = tree[0]
    for level, _ in enumerate(tree_path):
        next_node = _get_node_from_tree(tree, tree_path, level+1)
        solution.append([current_node, next_node])
        current_node = next_node
    return solution


def get_all_tree_paths(tree):
    """Return list of all tree paths
    """
    def rec(tree, tree_path):
        if len(tree) == 1:
            return [tree_path]
        branches = tree[1:]
        tree_paths = []
        for node, branch in enumerate(branches):
            tmp_tree_paths = (rec(branch, tree_path + [node+1]))
            tree_paths += tmp_tree_paths
        return tree_paths
    return rec(tree, [])


def get_all_solutions_from_tree(tree):
    """Return all half solution from the tree
    """
    if len(tree) == 0:
        return []

    def rec(tree, sol):
        if len(tree) == 1:
            return [sol]
        branches = tree[1:]
        solutions = []
        for branch in branches:
            solutions += rec(branch, sol + [branch[0]])
        return solutions
    return rec(tree, [tree[0]])


def _get_level_branch_nb(tree, tree_path, level):
    """Get number of branch at level
    """
    next_tree = copy.deepcopy(tree)
    for i in range(level):
        next_tree = next_tree[tree_path[i]]
    return len(next_tree)


def _get_branches(tree, tree_path, impact_level):
    """Return the new branches of the new tree path at impact level
    """
    next_tree = copy.deepcopy(tree)
    for i in range(impact_level):
        next_tree = next_tree[tree_path[i]]
    return next_tree[1:]


def _get_tree_max_level(tree):
    """Return the maximum level of the tree
    """
    if len(tree) == 1:
        return 0
    branches = tree[1:]
    max_level = 0
    for branch in branches:
        max_level = max(max_level, _get_tree_max_level(branch))
    return max_level


def get_tree_neighbor(tree, tree_path: list, level):
    """Return a tree neighbor of this level
    """
    modulo = _get_level_branch_nb(tree, tree_path, level)
    max_level = _get_tree_max_level(tree)
    new_tree_path = tree_path.copy()
    new_tree_path[level] = ((new_tree_path[level] + 1) % modulo)
    if new_tree_path[level] == 0:
        new_tree_path[level] = 1
    # impact on lower branch
    for impact_level in range(level, max_level):
        new_branches = _get_branches(tree, new_tree_path, impact_level)
        previous_next_node = _get_node_from_tree(
            tree, tree_path, impact_level + 1)
        for i in range(len(new_branches)):
            if previous_next_node in new_branches[i]:
                new_tree_path.append(i + 1)
        new_tree_path[level+1] = new_tree_path[level+1] % len(new_branches)
        if new_tree_path[level+1] == 0:
            new_tree_path[level+1] = 1
    # filling until finish point
    finish_point = _get_node_from_tree(tree, new_tree_path, len(new_tree_path))
    previous_finish_point = _get_node_from_tree(
        tree, tree_path, len(tree_path))
    while finish_point != previous_finish_point:
        level = len(new_tree_path)
        branches = _get_branches(tree, new_tree_path, level)
        new_tree_path.append(random.randint(1, len(branches)))
        finish_point = branches[new_tree_path[-1]-1][0]
    return new_tree_path
