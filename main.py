from state import State
import random


def test_hash_distribution(n_trials):
    tot = 0
    seed_offset = random.randint(1, 10000000)
    for i in range(1, n_trials+1):
        state = State(2, seed=i+seed_offset)
        tot += state._uniform_hash("hello")
    return tot/n_trials


def main():
    # print(test_hash_distribution(1000000))
    state = State(2, 10)
    print(state)
    
    while not state.is_terminal():
        print(state.actions())
        state = state.make(random.randint(0, 1))
        print(state)

main()
