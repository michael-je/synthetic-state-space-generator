import random
from State import State
from RNGHasher import RNGHasher
from custom_types import *
from custom_types import RandomnessDistribution as Dist
from example_functions import *
from default_functions import *
from collections import defaultdict

def print_histogram(hist: defaultdict[float|int, int]):
    hist_width = 80
    high = max(hist.values())
    low = min(hist.values())
    hist_range = high - low
    for k in sorted(hist.keys()):
        print("{:>5}: ".format(k) + '*' * int(hist_width * hist[k] / hist_range))


def test_hash_average(n_trials: int):
    tot = 0
    seed = random.randint(1, 10000000)
    hasher = RNGHasher(distribution=Dist.UNIFORM, seed=seed)
    for _ in range(1, n_trials+1):
        tot += hasher.next_float()
    print("test_hash_average:", tot/n_trials)


def test_gaussian_float_distribution(n_trials: int, decimal_accuracy: int=2, seed: int=0):
    histogram: defaultdict[float, int] = defaultdict(lambda: 0)
    hasher = RNGHasher(distribution=Dist.GAUSSIAN, seed=seed)
    for _ in range(n_trials):
        result = hasher.next_float()
        histogram[round(result, decimal_accuracy)] += 1
    print_histogram(histogram)


def test_gaussian_int_distribution(n_trials: int, dist_range: int=50, seed: int=0):
    histogram: defaultdict[float, int] = defaultdict(lambda: 0)
    hasher = RNGHasher(distribution=Dist.GAUSSIAN, seed=seed)
    for _ in range(n_trials):
        result = hasher.next_int(low=0, high=dist_range)
        histogram[result] += 1
    print_histogram(histogram)


def test_hash_uniformity(n_trials: int):
    # use numpy and binning to visualize uniformity
    pass


def test_deterministic_graph_1(seed: int=0):
    state = State(seed=seed, max_depth=10, retain_tree=True)
    test_deterministic_graph(state)

def test_deterministic_graph_2(seed: int=0):
    state = State(seed=seed, max_depth=20, branching_factor_base=3, branching_factor_variance=2, retain_tree=True)
    test_deterministic_graph(state)

# def test_deterministic_graph_2(seed: int=0):
#     state = State(seed=seed, max_depth=50, retain_tree=True, branching_function=lambda _, randf, __: 1+int(randf()*5))
#     test_deterministic_graph(state)

# def test_deterministic_graph_3(seed: int=0):
#     state = State(
#         seed=seed, 
#         max_depth=20, 
#         retain_tree=True, 
#         child_depth_function=child_depth_function_example_2,
#         transposition_space_function=transposition_space_function_example_1
#     )
#     test_deterministic_graph(state)

def test_deterministic_graph(state: State):
    try:
        while state._current.depth < state.globals.vars.max_depth - 1:
            while state._RNG.next_float() < 0.3 and not state.is_root():
                state.undo()
            while state._RNG.next_float() < 0.6 and not state.is_terminal():
                state.make_random()
                # state._current.generate_children()
    except KeyboardInterrupt:
        pass
    finally:
        state.draw()


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
    state.draw()


def test_ids(seed: int=0):
    state=State(seed=random.randint(0, 100), retain_tree=True)
    for _ in range(40):
        state.make_random()
        print(state)
    state.draw()



##Symmetry tests

def dfs(state: State, maxD: int, s: bool=False):

    visited = set()
    depthDensity = {i:0 for i in range(maxD+1)}

    def dfs_recur(state: State, currDepth: int):
        state_id = state.id()
        if state_id in visited:
            return
        
        visited.add(state_id)
        
        depthDensity[currDepth] += 1
        actions = state.actions()

        for action in actions:
            state.make(action)
            dfs_recur(state, currDepth+1)
            state.undo()

    dfs_recur(state, 0)

    for depth in depthDensity:
        print(f"{depth} : {depthDensity[depth]}")

    print()
    if not s:
        for depth in depthDensity:
            print(f"{depth} : {depthDensity[depth]/8}")

    print()
       


def test_symmytrical_graph():
    maxD = 9
    state = State(max_depth=maxD, branching_factor_base=2, symmetry=0.000000000000001, retain_tree=True)

    state = State(
        max_depth=10,
        root_value=0,
        branching_function=tictactoe_branching_function,
        child_value_function=tictactoe_child_value_function,
        child_depth_function=default_child_depth_function,
        transposition_space_function=tictactoe_transposition_space_function,
        seed=0,
        retain_tree=True
    )

    dfs(state, maxD)

    state1 = State(
        max_depth=10,
        root_value=0,
        symmetry=1/8,
        branching_function=tictactoe_branching_function,
        child_value_function=tictactoe_child_value_function,
        child_depth_function=default_child_depth_function,
        transposition_space_function=tictactoe_transposition_space_function,
        seed=0,
        retain_tree=True
    )

    dfs(state1, maxD, s=True)