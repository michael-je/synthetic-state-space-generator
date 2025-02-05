from State import State
import random


def test_hash_distribution(n_trials):
    tot = 0
    seed_offset = random.randint(1, 10000000)
    for i in range(1, n_trials+1):
        state = State(2, seed=i+seed_offset)
        tot += state._uniform_hash("hello")
    return tot/n_trials


def main():
    d = 20 # depth
    b = 3  # branching factor
    state = State(b, d)
    print(state)
    
    i = 0
    while not state.is_terminal():
        print(state.actions())
        state.make(i)
        if random.random() < 0.5:
            state.undo()
        else:
            i = (i + 1) % 3
        print(state)
        

main()
