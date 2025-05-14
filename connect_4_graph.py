import time
from example_functions import *
from default_functions import *
from State import State
from math import comb
import random
from State import State
from RNGHasher import RNGHasher
from example_functions import *
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
from collections import defaultdict

from collections import defaultdict

from collections import defaultdict

def dfs(state: State):
    parents_map = defaultdict(set)         # child_id -> set of parent_ids
    depth_map = defaultdict(set)           # depth -> set of unique state_ids
    terminal_count = defaultdict(int)      # depth -> count of terminal states
    branching_factor_sum = defaultdict(int)# depth -> sum of branching factors
    state_visits = set()                   # (state_id, depth) to avoid infinite loops

    def dfs_recur(current_state: State, depth: int, parent_id: str | None):
        sid = str(current_state.id())

        if parent_id is not None:
            parents_map[sid].add(parent_id)

        depth_map[depth].add(sid)

        state_key = (sid, depth)
        if state_key in state_visits:
            return
        state_visits.add(state_key)

        if current_state.is_terminal():
            terminal_count[depth] += 1
            return

        actions = current_state.actions()
        branching_factor_sum[depth] += len(actions)

        for action in actions:
            current_state.make(action)
            dfs_recur(current_state, depth + 1, sid)
            current_state.undo()

    dfs_recur(state, 0, None)

    print("#####################################")
    print("Transposition density by depth")
    print("-------------------------------------")
    max_depth = max(depth_map.keys())
    for d in range(max_depth + 1):
        transposition_count = defaultdict(int)  # num_parents -> count of states
        for sid in depth_map[d]:
            num_parents = max(1, len(parents_map[sid]))  # Ensure minimum is 1
            transposition_count[num_parents] += 1
        line = f"{d:>2} "
        for tp, count in sorted(transposition_count.items()):
            line += f"{count:>5} states with {tp:>2} transpositions, "
        print(line.rstrip(', '))
    
    print("\n#####################################")
    print("Terminal state count per depth")
    for d in range(max_depth + 1):
        print(f"{d:>2}: {terminal_count[d]:>5} terminal states")

    print("\n#####################################")
    print("Unique state count per depth")
    for d in range(max_depth + 1):
        print(f"{d:>2}: {len(depth_map[d]):>5} unique states")

    print("\n#####################################")
    print("Average branching factor per depth")
    for d in range(max_depth + 1):
        num_states = len(depth_map[d])
        if num_states > 0:
            avg_bf = branching_factor_sum[d] / num_states
            print(f"{d:>3}: {avg_bf:>6.3f} average branching factor")
        else:
            print(f"{d:>3}:    N/A")

    print("#####################################################")
    print("#####################################################")
    print()

    print("\n#####################################")
    print("Depth-wise terminal ratio, count, unique states, and avg branching factor")
    print("Depth | Terminal Ratio | Terminals | Unique States | Avg BF")
    print("------------------------------------------------------------")

    for d in range(max_depth + 1):
        terminals = terminal_count[d]
        unique = len(depth_map[d])
        total_non_terminals = max(1, unique - terminals)
        ratio = terminals / total_non_terminals if total_non_terminals else 1.0
        if unique > 0:
            avg_bf = branching_factor_sum[d] / unique
            print(f"{d:>5} |     {ratio:>6.3f}      |   {terminals:>7}  |     {unique:>6}     |  {avg_bf:>6.3f}")
        else:
            print(f"{d:>5} |     {ratio:>6.3f}      |   {terminals:>7}  |     {unique:>6}     |   N/A")




def tictactoeExample():

    state = State(
        seed = 3,
        max_depth=11,  #max_depth = 11 is ca 10 min to run
        branching_function=branching_function_connect_four,
        transposition_space_function=transposition_space_function_connect_four_2,
        # true_value_tie_chance=0,
        # true_value_forced_ratio=1,
        # true_value_similarity_chance=1,
        # locality=0.0
    )
        
    dfs(state)


def Connect_four_Example_2():
    state = State(
        max_depth = 10,
        branching_factor_base=7,
        branching_factor_variance=0,
        terminal_minimum_depth=7,
        terminal_chance=0.01,
        symmetry_factor=0.5,
        symmetry_frequency=0.4,
    )
    dfs(state)


start = time.time()
Connect_four_Example_2()

end = time.time()
print(f"Execution time: {end - start:.4f} seconds")