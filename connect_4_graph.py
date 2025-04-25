import random
from State import State
from RNGHasher import RNGHasher
from example_functions import *
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter


def test_connect_4(seed: int=0):
    md = 42


    state = State(seed = 1, max_depth=md, retain_tree = False, branching_function = branching_function_connect_four, transposition_space_function=transposition_space_function_connect_four)

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