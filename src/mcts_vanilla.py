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

    # helper function for finding the score
    def calculate_score(i):
        return (i.wins / i.visits) + (explore_faction * sqrt(log(i.parent.visits) / i.visits))
    

    leaf_node = node

    while not leaf_node.untried_actions and leaf_node.child_nodes:

        # find the best child move for this node
        leaf_node = list(leaf_node.child_nodes.values())[0]
        best_score = calculate_score(leaf_node)

        for i in leaf_node.child_nodes.values():
            current_score = calculate_score(i)
            #print(str(i) + str(current_score))

            if current_score > best_score:
                best_score = current_score
                leaf_node = i
    
        state = board.next_state(state, leaf_node.parent_action)
        #print(">>> Next Layer from {}".format(leaf_node))
        

    if leaf_node.untried_actions:
        # expand the tree if current node been visited
        return expand_leaf(leaf_node, board, state)

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
    state = board.next_state(state, next_action)

    #print("-all actions-")
    #print(node.untried_actions)
    #print("< add leaf at {}".format(next_action))

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
    
    return board.points_values(curr_state)


def backpropagate(node, won):
    """ Navigates the tree from a leaf node to the root, updating the win and visit count of each node along the path.

    Args:
        node:   A leaf node.
        won:    An indicator of whether the bot won or lost the game.

    """

    # Updates number of visits
    node.visits += 1 
    # Updates number of wins
    if won:
        node.wins += 1
    # If not root, step closer to root       
    if node.parent is not None:
        #print(">>>Hey going from {} to {}".format(str(node), str(node.parent)))
        backpropagate(node.parent, won)
        


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

        # MCTS
        leaf = traverse_nodes(node, board, sampled_game, identity_of_bot)
        
        result = True if rollout(board, sampled_game)[identity_of_bot] > 0 else False
        backpropagate(leaf, result)

        #print("Final Leaf {}".format(leaf))
        #print("---- Current Step {} Finished ----".format(step))


    # check for the best action
    # [BUGGED] can't select the most frequently used action
    #print("All avaliable actions:")
    #print(root_node.child_nodes.keys())

    # helper for finding win rate
    def node_winrate(node):
        return node.wins/node.visits

    # determine the best action by win rate (win/visits)
    best_action = list(root_node.child_nodes.keys())[0]
    best_win_rate = node_winrate(root_node.child_nodes[best_action])

    for action in root_node.child_nodes:
        new_win_rate = node_winrate(root_node.child_nodes[action])

        if new_win_rate > best_win_rate:
            best_win_rate = new_win_rate
            best_action = action

        
    # Return an action, typically the most frequently used action (from the root) or the action with the best
    # estimated win rate.
    return best_action
