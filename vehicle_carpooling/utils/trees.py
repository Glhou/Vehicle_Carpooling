# vehicle_carpooling/utils/trees.py

"""Utils for trees
"""

import numpy as np
import copy
import random


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
            next_node, finish_point, nb_steps-1, next_node)
        if next_tree[0] == finish_point:
            tree.append(next_tree)
        elif not next_tree[1]:  # if there is branches
            tree.append(next_tree)
    return [node, *tree]


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
    for level, node in enumerate(tree_path):
        next_node = _get_node_from_tree(tree, tree_path, level)
        solution.append((current_node, next_node))
        current_node = next_node
    return solution


def _get_level_branch_nb(tree, tree_path, level):
    """Get number of branch at level
    """
    next_tree = copy.deepcopy(tree)
    for i in range(level):
        next_tree = next_tree[tree_path[i]]
    return len(next_tree) - 1  # remove the node


def _get_branches(tree, tree_path, impact_level):
    """Return the new branches of the new tree path at impact level
    """
    next_tree = copy.deepcopy(tree)
    for i in range(impact_level):
        next_tree = next_tree[tree_path[i]]
    return next_tree[1:]


def get_tree_neighbor(tree, tree_path: list, level):
    """Return a tree neighbor of this level
    """
    modulo = _get_level_branch_nb(tree, tree_path, level)
    new_tree_path = tree_path.copy()
    new_tree_path[level] = (new_tree_path[level] + 1) % modulo
    # impact on lower branch
    for impact_level in range(level, len(tree_path)):
        new_branches = _get_branches(tree, new_tree_path, impact_level)
        previous_next_node = _get_node_from_tree(
            tree, tree_path, impact_level + 1)
        for i in range(len(new_branches)):
            if previous_next_node in new_branches[i]:
                new_tree_path[level+1] = i + 1
        new_tree_path[level+1] = new_tree_path[level+1] % len(new_branches)
    finish_point = _get_node_from_tree(tree, new_tree_path, len(new_tree_path))
    previous_finish_point = _get_node_from_tree(
        tree, tree_path, len(tree_path))
    while finish_point != previous_finish_point:
        level = len(new_tree_path) + 1
        branches = _get_branches(tree, new_tree_path, level)
        new_tree_path.append(random.randint(1, len(branches)))
        finish_point = branches[new_tree_path[-1]][0]
    return new_tree_path
