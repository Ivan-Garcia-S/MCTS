Sam Feng - yfeng68
Ivan Garcia-Sanchez - igarci33

Modifications for mcts_modified.py

In the rollout phase of the MCTS search, we made it so that 40% of the time, instead of chooisng a random action to take from the current state, rollout would first search to see if either the center space or any of the four corner spaces were available. If so, there would be a random selection from this set of actions.  If none are found, proceed to select a random action just like in the mcts_vanilla implementation.