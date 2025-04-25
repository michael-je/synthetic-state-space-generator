import random
from State import State
from RNGHasher import RNGHasher
from example_functions import *
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter



def test_hash_average(n_trials:int ):
    tot = 0
    seed = random.randint(1, 10000000)
    hasher = RNGHasher(seed=seed)
    for _ in range(1, n_trials+1):
        tot += hasher.next_uniform()
    print("test_hash_average:", tot/n_trials)


def test_hash_uniformity(n_trials: int):
    # use numpy and binning to visualize uniformity
    pass


def test_deterministic_graph_1(seed: int=0):
    md = 10
    state = State(seed=seed, max_depth=md, retain_tree=True, child_depth_function=child_depth_function_example_2, transposition_space_function=transposition_space_function_example_1)
    test_deterministic_graph(state, md)

def test_deterministic_graph_2(seed: int=0):
    md = 50
    state = State(seed=seed, max_depth=md, retain_tree=True, branching_function=lambda _, randf, __: 1+int(randf()*5))
    test_deterministic_graph(state, md)

def test_deterministic_graph_3(seed: int=0):
    md = 20
    state = State(
        seed=seed, 
        max_depth=md, 
        retain_tree=True, 
        child_depth_function=child_depth_function_example_2,
        transposition_space_function=transposition_space_function_example_1
    )
    test_deterministic_graph(state, md)

def test_deterministic_graph(state: State, max_depth: int):
    try:
        while state._current.depth < max_depth - 1:
            while state._RNG.next_uniform() < 0.3 and not state.is_root():
                state.undo()
            while state._RNG.next_uniform() < 0.6 and not state.is_terminal():
                state.make_random()
                # state._current.generate_children()
    except KeyboardInterrupt:
        pass
    finally:
        state.draw_tree()


def test_random_graph(retain_tree: bool=True):
    b = random.randint(2, 5)
    d = random.randint(5, 15)
    state = State(b, d, retain_tree=retain_tree)
    while not state.is_terminal():
        while random.random() < 0.5 and not state.is_root():
            state.undo()
        while random.random() < 0.6 and not state.is_terminal():
            state.make(random.randint(0, b-1))
            state._current.generate_children()
    state.draw_tree()


def test_ids(seed: int=0):
    state=State(seed=random.randint(0, 100), retain_tree=True)
    for _ in range(40):
        state.make_random()
        print(state)
    state.draw_tree()








from collections import deque, defaultdict

def bfs(state: State):
    visited = set()
    queue = deque([(state._root, 0)])  # node paired with its depth level
    visited.add(state._root.id)

    terminals_by_level = defaultdict(int)
    non_terminals_by_level = defaultdict(int)
    unique_states_by_level = defaultdict(set)
    branching_factors = defaultdict(list)
    parent_counts_by_level = defaultdict(lambda: defaultdict(int))  # level -> parent count -> number of nodes
    parent_tracker = defaultdict(set)  # node id -> set of parent ids

    while queue:
        current_node, level = queue.popleft()

        # Generate children explicitly
        current_node.generate_children()

        # Track unique states
        unique_states_by_level[level].add(current_node.id)

        # Record branching factor
        branching_factors[level].append(len(current_node.children))

        # Terminal node check
        if current_node.is_terminal():
            terminals_by_level[level] += 1
        else:
            non_terminals_by_level[level] += 1

        for child in current_node.children:
            parent_tracker[child.id].add(current_node.id)
            if child.id not in visited:
                queue.append((child, level + 1))
                visited.add(child.id)

    # Count parent multiplicity per level
    for node_id, parents in parent_tracker.items():
        parent_count = len(parents)
        for level, nodes in unique_states_by_level.items():
            if node_id in nodes:
                parent_counts_by_level[level][parent_count] += 1

    for level in sorted(set(terminals_by_level.keys()).union(non_terminals_by_level.keys())):
        terminal_count = terminals_by_level.get(level, 0)
        non_terminal_count = non_terminals_by_level.get(level, 0)
        unique_state_count = len(unique_states_by_level.get(level, set()))
        avg_branching = (sum(branching_factors[level]) / len(branching_factors[level])) if branching_factors[level] else 0
        print(f"Level {level}: {terminal_count} terminal nodes, {non_terminal_count} non-terminal nodes, {unique_state_count} unique states, average branching factor: {avg_branching:.5f}")

        parent_counts = parent_counts_by_level[level]
        for parent_count in sorted(parent_counts.keys()):
            print(f"    Nodes with {parent_count} parent(s): {parent_counts[parent_count]}")

def bfs_2(state: State):
    visited = set()
    queue = deque([(state._root, 0)])  # node paired with its depth level
    visited.add(state._root.id)

    terminals_by_level = defaultdict(int)
    non_terminals_by_level = defaultdict(int)
    unique_states_by_level = defaultdict(set)
    branching_factors = defaultdict(list)
    parent_counts_by_level = defaultdict(lambda: defaultdict(int))  # level -> parent count -> number of nodes
    parent_tracker = defaultdict(set)  # node id -> set of parent ids
    node_levels = {}  # node id -> level
    parent_count_total_by_level = defaultdict(int)  # level -> total number of parent links
    random_bits_by_level = defaultdict(list)  # level -> list of random bits
    transposition_space_by_level = {}  # level -> transposition space size

    def extract_random_bits(node_id: int, depth: int, globals) -> int:
        return node_id & (globals.transposition_space_map[depth] - 1)

    while queue:
        current_node, level = queue.popleft()
        node_id = current_node.id

        # Track level of this node
        if node_id not in node_levels:
            node_levels[node_id] = level

        # Track unique states
        unique_states_by_level[level].add(node_id)

        # Terminal node check
        if current_node.is_terminal():
            terminals_by_level[level] += 1
        else:
            non_terminals_by_level[level] += 1

        # Generate children explicitly
        current_node.generate_children()

        # Record branching factor
        branching_factors[level].append(len(current_node.children))

        for child in current_node.children:
            child_id = child.id
            parent_tracker[child_id].add(node_id)
            child_level = level + 1
            parent_count_total_by_level[child_level] += 1

            # Always record the minimum level among all parent paths
            if child_id not in node_levels or child_level < node_levels[child_id]:
                node_levels[child_id] = child_level

            # Extract and record random bits of child ID
            random_bits = extract_random_bits(child_id, child.depth, child.globals)
            random_bits_by_level[child_level].append(random_bits)

            # Track transposition space size for this level (used to compute missing)
            transposition_space_by_level[child_level] = child.globals.transposition_space_map[child.depth]

            if child_id not in visited:
                visited.add(child_id)
                queue.append((child, child_level))

    # Count parent multiplicity per level using corrected node_levels
    for node_id, parents in parent_tracker.items():
        parent_count = len(parents)
        level = node_levels.get(node_id)
        if level is not None:
            parent_counts_by_level[level][parent_count] += 1

    all_levels = sorted(set(
        terminals_by_level.keys()
        ).union(
        non_terminals_by_level.keys()
        ).union(
        unique_states_by_level.keys()
    ))

    for level in all_levels:
        terminal_count = terminals_by_level.get(level, 0)
        non_terminal_count = non_terminals_by_level.get(level, 0)
        unique_state_count = len(unique_states_by_level[level])
        avg_branching = (
            sum(branching_factors[level]) / len(branching_factors[level])
            if branching_factors[level] else 0
        )

        total_parents = parent_count_total_by_level[level]

        print(f"Level {level}: {terminal_count} terminal nodes, {non_terminal_count} non-terminal nodes, {unique_state_count} unique states, average branching factor: {avg_branching:.2f}, total parents: {total_parents}")

        for parent_count in sorted(parent_counts_by_level[level].keys()):
            print(f"    Nodes with {parent_count} parent(s): {parent_counts_by_level[level][parent_count]}")

        if random_bits_by_level[level]:
            sorted_bits = sorted(random_bits_by_level[level])
            print(f"    Random bits: {sorted_bits}")
            if level >= 3:
                space_size = transposition_space_by_level.get(level)
                if space_size:
                    full_set = set(range(space_size))
                    used_set = set(sorted_bits)
                    missing = sorted(full_set - used_set)
                    print(f"    Missing random bits: {missing}")


def bfs_3(state: State):
    visited = set()
    queue = deque([state._root])
    visited.add(state._root.id)

    terminal_nodes = 0


    while queue:
        current_node = queue.popleft()

        current_node.generate_children()

                # Terminal node check
        if current_node.is_terminal():
            terminal_nodes += 1

        for child in current_node.children:
            if child.id not in visited:
                queue.append(child)
                visited.add(child.id)

    print(f"Total number of terminal nodes: {terminal_nodes}")


def test_tictactoe(seed: int=0):
    md = 10


    state = State(seed = 1, max_depth=md, retain_tree = False, branching_function = branching_function_tictactoe, transposition_space_function=transposition_space_function_tictactoe)



    bfs_2(state)


    try:
        while state._current.depth < md - 1:
            while state._RNG.next_uniform() < 0.8 and not state.is_root():
                state.undo()
            while state._RNG.next_uniform() < 0.6 and not state.is_terminal():
                state.make_random()
                # state._current.generate_children()
    except KeyboardInterrupt:
        pass
    finally:
        state.draw_tree()







        




