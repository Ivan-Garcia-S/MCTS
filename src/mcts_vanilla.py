
from mcts_node import MCTSNode
from random import choice
from math import sqrt, log

num_nodes = 1000
explore_faction = 2.

def traverse_nodes(node, board, state, identity):
    """ Traverses the tree until the end criterion are met.

    Args:
        node:       A tree node from which the search is traversing.
        board:      The game setup.
        state:      The state of the game.
        identity:   The bot's identity, either 'red' or 'blue'.

    Returns:        A node from which the next stage of the search can proceed.

    """
    leaf_node = node

    # keep finding until leaf_node is never visited or it doesn't have children
    while leaf_node.child_nodes and leaf_node.visits != 0:

        best_score = 0
        for i in leaf_node.child_nodes.values():
            # UCT calculate the score
            current_score = (i.wins / i.visits) + (explore_faction * sqrt(log(leaf_node.visits) / i.visits))
            print(str(i))
            print(current_score)

            if current_score > best_score:
                best_score = current_score
                leaf_node = i
        
    return leaf_node


def expand_leaf(node, board, state):
    """ Adds a new leaf to the tree by creating a new child node for the given node.

    Args:
        node:   The node for which a child will be added.
        board:  The game setup.
        state:  The state of the game.

    Returns:    The added child node.

    """
    next_action = node.untried_actions.pop(0)
    new_node = MCTSNode(parent=node, parent_action=next_action, action_list=board.legal_actions(state))
    
    # add it back in the node
    node.child_nodes[next_action] = new_node

    return new_node


def rollout(board, state):
    """ Given the state of the game, the rollout plays out the remainder randomly.

    Args:
        board:  The game setup.
        state:  The state of the game.

    """
    curr_state = state
    while not board.is_ended(curr_state):
        random_action = choice(board.legal_actions(curr_state))
        curr_state = board.next_state(curr_state, random_action)


def backpropagate(node, won):
    """ Navigates the tree from a leaf node to the root, updating the win and visit count of each node along the path.

    Args:
        node:   A leaf node.
        won:    An indicator of whether the bot won or lost the game.

    """
    print("Node", node)
    # Updates number of visits
    node.visits += 1 
    # Updates number of wins
    if won:
        node.wins += 1
    # If not root, step closer to root       
    if node.parent is not None:
        backpropagate(node.parent, not won)
        


def think(board, state):
    """ Performs MCTS by sampling games and calling the appropriate functions to construct the game tree.

    Args:
        board:  The game setup.
        state:  The state of the game.

    Returns:    The action to be taken.

    """
    identity_of_bot = board.current_player(state)
    root_node = MCTSNode(parent=None, parent_action=None, action_list=board.legal_actions(state))

    for step in range(num_nodes):
        # Copy the game for sampling a playthrough
        sampled_game = state

        # Start at root
        node = root_node

        # Very Cool MCTS
        leaf = traverse_nodes(node, board, sampled_game, identity_of_bot)
        new_node = expand_leaf(leaf, board, sampled_game)
        rollout(board, sampled_game)

        result = True if board.points_values(sampled_game)[identity_of_bot] > 0 else False
        backpropagate(new_node, result)


    # check what's the best action
    best_action = root_node.child_nodes[root_node.child_nodes.keys()[0]]
    for action in root_node.child_nodes:
        if root_node.child_nodes[action].wins > root_node.child_nodes[best_action].wins:
            best_action = action

        
    # Return an action, typically the most frequently used action (from the root) or the action with the best
    # estimated win rate.
    return best_action
