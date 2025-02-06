import random
from State import State


def state_representative(state: State):
    type = state._current.node_type.name
    actions = state.actions()
    return type, actions


def compare_representatives(state1: State, state2: State):
    return state1[0] == state2[0] and state1[1] == state2[1]


def test_hash_average(n_trials):
    tot = 0
    seed_offset = random.randint(1, 10000000)
    for i in range(1, n_trials+1):
        state = State(2, 1, seed=i+seed_offset,)
        tot += state._current._uniform_hash("hello")
    print("test_hash_average:", tot/n_trials)
    print()


def test_hash_uniformity(n_trials):
    # use numpy and binning to visualize uniformity
    pass


def test_undo():
    results = []
    state = State(10, 100, node_type_ratio=1)
    while not state.is_terminal():
        state.make(0)
        if random.random() < 0.5:
            before_undo = state_representative(state)
            state.undo()
            state.make(0)
            after_undo = state_representative(state)
            result = compare_representatives(before_undo, after_undo)
            results.append(result)
    
    test_result = all(results)
    print("test_undo:", test_result)
    if not test_result:
        print(results)
    print()


def test_deterministic(b, d):
    def run_trial():
        state = State(b, d)
        steps = []
        i = 0
        while not state.is_terminal():
            state.make(i)
            if random.random() < 0.5:
                state.undo()
            else:
                steps.append(state_representative(state))
                i = (i + 1) % 3
        return steps
    
    steps1 = run_trial()
    steps2 = run_trial()
    test_result = all(compare_representatives(*z) for z in zip(steps1, steps2))
    print("test_deterministic", test_result)
    if not test_result:
        for step in zip(steps1, steps2):
            print(step)


def test_deterministic_graph(seed: int=0, retain_tree: bool=True):
    b = 5
    d = 15
    state = State(b, d, seed=seed, retain_tree=retain_tree)
    while not state.is_terminal():
        while state.hasher.next_random() < 0.5 and not state.is_root():
            state.undo()
        while state.hasher.next_random() < 0.6 and not state.is_terminal():
            state.make_random()
            state._current.generate_children()
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
