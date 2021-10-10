from timeit import default_timer as time
from mcts_node import MCTSNode
from random import choice, randint
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
    new_state = state
    
    # else search through the childs
    while not leaf_node.untried_actions and leaf_node.child_nodes:
            
        # find the best child move for this node
        best_score = 0

        for i in leaf_node.child_nodes.values():

            if leaf_node.visits != 0:
                current_score = calculate_score(i)
            else:
                current_score = 0
            
            #print(str(i) + str(current_score))

            if current_score >= best_score:
                best_score = current_score
                leaf_node = i
    
        if leaf_node.parent_action:
            new_state = board.next_state(new_state, leaf_node.parent_action)

        #print(">>> Next Layer from {}".format(leaf_node))

    # expand the tree if current node have more untried actions
    if leaf_node.untried_actions:
        leaf_node, new_state = expand_leaf(leaf_node, board, new_state)

    return leaf_node, new_state


def expand_leaf(node, board, state):
    """ Adds a new leaf to the tree by creating a new child node for the given node.

    Args:
        node:   The node for which a child will be added.
        board:  The game setup.
        state:  The state of the game.

    Returns:    The added child node.

    """
    # expand on a random action
    next_action = choice(node.untried_actions)
    node.untried_actions.remove(next_action)

    new_state = board.next_state(state, next_action)

    #print("-all actions-")
    #print(node.untried_actions)
    #print("< add leaf at {}".format(next_action))

    new_node = MCTSNode(parent=node, parent_action=next_action, action_list=board.legal_actions(new_state))
    
    # add it back in the node
    node.child_nodes[next_action] = new_node

    return new_node, new_state


def rollout(board, state):
    """ Given the state of the game, the rollout plays out the remainder randomly.

    Args:
        board:  The game setup.
        state:  The state of the game.

    Returns:    The end state of the game.

    """
    curr_state = state
    while not board.is_ended(curr_state):
        rand = randint(1,10)
        # Looks for available corner and center moves 40% of the time
        if rand > 6:
            corner_found = False 
            for action in board.legal_actions(curr_state):
                # Looks for available corner space or center space
                if ((action[2] == 0 and action[3] == 0) or (action[2] == 0 and action[3] == 2) or \
                                         (action[2] == 2 and action[3] == 0) or (action[2] == 2 and action[3] == 2) or\
                                          action[2] == 1 and action[3] == 1) and not corner_found:
                    final_action = action
                    corner_found = True
            if not corner_found:
                final_action = choice(board.legal_actions(curr_state))
        else:      
            final_action = choice(board.legal_actions(curr_state))
        curr_state = board.next_state(curr_state, final_action)
    
    return curr_state


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

    start = time()
    time_elapsed = time() - start

    num_nodes = 0

    while time_elapsed <= 0.2:
        num_nodes += 1

        # Copy the game for sampling a playthrough
        sampled_game = state

        # Start at root
        node = root_node

        # MCTS
        leaf, sampled_game = traverse_nodes(node, board, sampled_game, identity_of_bot)
        
        result_state = rollout(board, sampled_game)

        result = True if board.points_values(result_state)[identity_of_bot] > 0 else False
        backpropagate(leaf, result)

        time_elapsed = time() - start

    print("Modified Tree Size: {}".format(num_nodes))

    # check for the best action
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
    
    #print("Choosed action {} with win rate of {}".format(best_action, best_win_rate))

        
    # Return an action, typically the most frequently used action (from the root) or the action with the best
    # estimated win rate.
    return best_action
