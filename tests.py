import unittest
import math
from collections import defaultdict
import mmh3

import RNGHasher
from RNGHasher import RNGHasher as RNG
from State import State
from custom_types import *
from custom_exceptions import *
from constants import *
from utils import *


class SeedGenerator():
    def __init__(self):
        self.hash_num = 0
    
    def __iter__(self):
        return self
    
    def __next__(self):
        hash_64bit, _ = mmh3.mmh3_x64_128_utupledigest("aaa".encode(), self.hash_num)
        self.hash_num += 1
        return hash_64bit % 100000

seeds = SeedGenerator()


class TestBitSize(unittest.TestCase):
    
    def test_bit_size(self):
        self.assertEqual(64, bit_size(2**64-1))
        self.assertEqual(65, bit_size(2**64))
        self.assertEqual(1,  bit_size(2**0))
        self.assertEqual(2,  bit_size(2**1))


class TestRNG(unittest.TestCase):

    def test_basic_rng_determinism(self):
        N_TRIALS = 10000
        for _ in range(100):
            seed = next(seeds)
            rng1 = RNG(distribution=RandomnessDistribution.UNIFORM, seed=seed)
            sequence1 = [rng1.next_int() for _ in range(N_TRIALS)]
            rng2 = RNG(distribution=RandomnessDistribution.UNIFORM, seed=seed)
            sequence2 = [rng2.next_int() for _ in range(N_TRIALS)]
            self.assertEqual(sequence1, sequence2)

    def test_hash_average(self):
        N_TRIALS = 100000
        for _ in range(10):
            rng = RNG(distribution=RandomnessDistribution.UNIFORM, seed=next(seeds))
            tot = 0
            for _ in range(1, N_TRIALS+1):
                tot += rng.next_float()
            average = tot/N_TRIALS
            self.assertAlmostEqual(0.5, average, places=2)
    
    def test_reset(self):
        for _ in range(100):
            rng = RNG(distribution=RandomnessDistribution.UNIFORM, seed=next(seeds))
            sequence1 = [rng.next_int() for _ in range(100)]
            rng.reset()
            sequence2 = [rng.next_int() for _ in range(100)]
            self.assertEqual(sequence1, sequence2)
    
    def test_gaussian_distribution(self):
        N_TRIALS = 1000000
        rng = RNG(distribution=RandomnessDistribution.GAUSSIAN)
        bins: defaultdict[int, float]= defaultdict(lambda: 0)
        for _ in range(N_TRIALS):
            n = rng.next_float(
                low=-RNGHasher.GAUSSIAN_MAX_DIST_FROM_MEAN, 
                high=RNGHasher.GAUSSIAN_MAX_DIST_FROM_MEAN)
            if n < -2:
                bins[-2] += 1
            elif n < -1:
                bins[-1] += 1
            elif n < 0:
                bins[0] += 1
            elif n < 1:
                bins[1] += 1
            elif n < 2:
                bins[2] += 1
            else:
                bins[3] += 1
        BAND_1 = 0.341
        BAND_2 = 0.136
        BAND_3 = 0.5 - BAND_1 - BAND_2
        self.assertAlmostEqual(bins[-2]/N_TRIALS, BAND_3, places=2)
        self.assertAlmostEqual(bins[-1]/N_TRIALS, BAND_2, places=2)
        self.assertAlmostEqual(bins[0]/N_TRIALS,  BAND_1, places=2)
        self.assertAlmostEqual(bins[1]/N_TRIALS,  BAND_1, places=2)
        self.assertAlmostEqual(bins[2]/N_TRIALS,  BAND_2, places=2)
        self.assertAlmostEqual(bins[3]/N_TRIALS,  BAND_3, places=2)
    
    def test_uniform_distribution(self):
        N_TRIALS = 1000000
        rng = RNG(distribution=RandomnessDistribution.UNIFORM)
        bins: defaultdict[int, int]= defaultdict(lambda: 0)
        low, high = 0, 10000
        for _ in range(N_TRIALS):
            n = rng.next_int(low=low, high=high)
            if n < high / 5:
                bins[1] += 1
            elif n < high * 2 / 5:
                bins[2] += 1
            elif n < high * 3 / 5:
                bins[3] += 1
            elif n < high * 4 / 5:
                bins[4] += 1
            else:
                bins[5] += 1
        MARGIN = N_TRIALS * 0.001
        for result in bins.values():
            self.assertLess(abs(result - N_TRIALS/5), MARGIN)
    
    def test_bad_int_arguments(self):
        rng = RNG(distribution=RandomnessDistribution.UNIFORM)
        # ranges too large
        self.assertRaises(ValueError, lambda: rng.next_int(high=HASH_OUTPUT_TMAX+1))
        self.assertRaises(ValueError, lambda: rng.next_int(low=-(HASH_OUTPUT_TMAX+1)))
        self.assertRaises(ValueError, lambda: rng.next_int(
            low=math.floor(-HASH_OUTPUT_TMAX/2), high=math.ceil(HASH_OUTPUT_TMAX/2)))
        # inverted ranges
        self.assertRaises(ValueError, lambda: rng.next_int(low=1, high=0))
        self.assertRaises(ValueError, lambda: rng.next_int(low=-5, high=-10))
        self.assertRaises(ValueError, lambda: rng.next_int(low=1000000, high=-100000))
        # float ranges
        self.assertRaises(ValueError, lambda: rng.next_int(low=0.1)) # type: ignore
        self.assertRaises(ValueError, lambda: rng.next_int(high=0.1)) # type: ignore
    
    def test_good_int_arguments(self):
        rng = RNG(distribution=RandomnessDistribution.UNIFORM)
        N_TRIALS = 10000
        # zero ranges
        ranges = (0, 100, -100)
        for r in ranges:
            self.assertEqual(r, rng.next_int(low=r, high=r))
        # very small ranges. Want to test if all values appear.
        ranges = ((-11, -10), (10000, 10001), (-1, 0), (-1, 1), (5, 8))
        for r in ranges:
            low, high = r
            results: list[int] = []
            for _ in range(N_TRIALS):
                results.append(rng.next_int(low=low, high=high))
            self.assertIn(low, results)
            self.assertIn(high, results)
        # very large ranges
        ranges = ((0, HASH_OUTPUT_TMAX), 
                  (-HASH_OUTPUT_TMAX, 0), 
                  (math.ceil(-HASH_OUTPUT_TMAX/2)+1, math.floor(HASH_OUTPUT_TMAX/2)))
        for r in ranges:
            low, high = r
            rng.next_int(low=low, high=high)
    
    def test_bad_float_arguments(self):
        rng = RNG(distribution=RandomnessDistribution.UNIFORM)
        # test low > high
        ranges = ((1, 0), (0.000000000001, 0), (-2, -3))
        for r in ranges:
            low, high = r
            self.assertRaises(ValueError, lambda: rng.next_float(low=low, high=high))

    def test_good_float_arguments(self):
        rng = RNG(distribution=RandomnessDistribution.UNIFORM)
        N_TRIALS = 10000
        # zero ranges
        ranges = (0.0, 0.000000000001, -123.123)
        for r in ranges:
            self.assertEqual(r, rng.next_float(low=r, high=r))
        # very small ranges
        ranges = ((-0.1, 0), 
                  (0, 0.000000000000000001), 
                  (0.00000000001, 0.0000000002))
        for r in ranges:
            low, high = r
            for _ in range(N_TRIALS):
                result = rng.next_float(low=low, high=high)
                self.assertTrue(low <= result <= high)
        # very large ranges
        ranges = ((0.0, HASH_OUTPUT_TMAX), 
                  (-HASH_OUTPUT_TMAX, 0), 
                  (-HASH_OUTPUT_TMAX/2, HASH_OUTPUT_TMAX/2))
        for r in ranges:
            low, high = r
            rng.next_float(low=low, high=high)


class TestState(unittest.TestCase):
    
    # TODO: test determinism with more complex graphs, especially where
    # we revisit states multiple times from different paths

    # def _default_test_states(self):
    #     return [
    #         State(max_depth=0),
    #         State(max_depth=1),
    #         State(max_depth=10000),
    #         State(branching_factor_base=10, max_depth=100),
    #     ]
    
    def _walk_graph(self, state: State, walk_seed: int=0):
        rng = RNG(distribution=RandomnessDistribution.UNIFORM, seed=walk_seed)
        while state.depth() < state.globals.vars.max_depth - 1:
            while rng.next_float() < 0.56 and not state.is_root():
                state.undo()
            while rng.next_float() < 0.6 and not state.is_terminal():
                state.make_random()

    def test_undo_root(self):
        state = State()
        self.assertRaises(RootHasNoParent, lambda: state.undo())
        state.make(state.actions()[0])
        state.undo()
        self.assertRaises(RootHasNoParent, lambda: state.undo())
    
    def test_make_terminal(self):
        state = State()
        while not state.is_terminal():
            state.make(0)
        self.assertRaises(TerminalHasNoChildren, lambda: state.make(0))
    
    def test_make_random(self):
        pass
    
    def test_depth(self):
        N_TRIALS = 100
        rng = RNGHasher.RNGHasher(RandomnessDistribution.UNIFORM)
        state = State(max_depth=10000)
        depth = 0
        self.assertEqual(state.depth(), depth)
        state.make_random()
        depth += 1
        # self.assertEqual(state.depth(), depth)
        for _ in range(N_TRIALS):
            steps = rng.next_int(
                low=-state.depth(), high=state.globals.vars.max_depth - state.depth())
            while steps < 0:
                state.undo()
                depth -= 1
                steps += 1
            while steps > 0:
                state.make_random()
                depth += 1
                steps -= 1
        self.assertEqual(state.depth(), depth)
    
    def test_state_parameter_ranges(self):
        self.assertRaises(ValueError, lambda: State(max_depth=-1))
        self.assertRaises(ValueError, lambda: State(max_depth=0))
        self.assertRaises(ValueError, lambda: State(max_depth=2**ID_BIT_SIZE))
        self.assertRaises(ValueError, lambda: State(child_depth_minumum=2, child_depth_maximum=1))
        self.assertRaises(ValueError, lambda: State(terminal_minimum_depth=-1))
        self.assertRaises(ValueError, lambda: State(branching_factor_base=-1))
        self.assertRaises(ValueError, lambda: State(branching_factor_variance=-1))
        # TODO
    
    def test_basic_state_determinism_1(self):
        state1 = State()
        self._walk_graph(state1)
        state1_id = state1.id()
        state2 = State()
        self._walk_graph(state2)
        state2_id = state2.id()
        self.assertEqual(state1_id, state2_id)
    
    def test_basic_state_determinism_2(self):
        N_TRIALS = 50
        DEPTH = 30
        state1 = State(max_depth=DEPTH)
        state2 = State(max_depth=DEPTH)
        for _ in range(N_TRIALS):
            self._walk_graph(state1, next(seeds))
            self._walk_graph(state2, next(seeds))
            while not state1.is_root():
                state1.undo()
            while not state2.is_root():
                state2.undo()
        while not state1.is_terminal():
            state1.make(state1.actions()[0])
        while not state2.is_terminal():
            state2.make(state2.actions()[0])
        self.assertEqual(state1.id(), state2.id())
    
    def test_maxdepth_1(self):
        state = State(max_depth=1)
        self.assertRaises(TerminalHasNoChildren, lambda: state.make_random())
    
    def test_negative_branching_function(self):
        state = State(branching_function=lambda *_: -1) # type: ignore
        self.assertRaises(TerminalHasNoChildren, lambda: state.make_random())
    
    def test_negative_child_depth(self):
        state = State(child_depth_function=lambda *_: -1) # type: ignore
        self.assertRaises(IdOverflow, lambda: state.make_random())
    
    def test_large_child_depth(self):
        state = State(max_depth=2, child_depth_function=lambda *_: 3) # type: ignore
        self.assertRaises(IdOverflow, lambda: state.make_random())
    
    def test_transposition_space_functions(self):
        # spaces too small
        state = State(transposition_space_function=lambda *_: 0) # type: ignore
        self.assertRaises(ValueError, lambda: state.make_random())
        state = State(transposition_space_function=lambda *_: -1) # type: ignore
        self.assertRaises(ValueError, lambda: state.make_random())
        # space barely large enough
        state = State(transposition_space_function=lambda *_: 1) # type: ignore
        state.make_random()
        # space at maximum
        mtss = State().globals.vars.max_transposition_space_size
        state = State(transposition_space_function=lambda *_: mtss) # type: ignore
        state.make_random()
        # space above maximum
        state = State(transposition_space_function=lambda *_: mtss+1) # type: ignore
        self.assertRaises(IdOverflow, lambda: state.make_random())
    
    def test_id_bit_partitioning_1(self):
        state = State(max_depth=2**(ID_BIT_SIZE-1)-1)
        self.assertEqual(2**1, state.globals.vars.max_transposition_space_size)
        state = State(max_depth=2**(ID_BIT_SIZE-2)-1)
        self.assertEqual(2**2, state.globals.vars.max_transposition_space_size)
        state = State(max_depth=2**(ID_BIT_SIZE-32)-1)
        self.assertEqual(2**32, state.globals.vars.max_transposition_space_size)
    
    def test_id_bit_partitioning_2(self):
        state1 = State(max_depth=2**(ID_BIT_SIZE-2))
        state2 = State(max_depth=2**(ID_BIT_SIZE-20))
        state3 = State(max_depth=2**(ID_BIT_SIZE-60))
        assert(
            state1.globals.vars.max_depth * state1.globals.vars.max_transposition_space_size == 
            state2.globals.vars.max_depth * state2.globals.vars.max_transposition_space_size == 
            state3.globals.vars.max_depth * state3.globals.vars.max_transposition_space_size
        )
    
    def test_str(self):
        state = State()
        self.assertEqual(str(state), "0-0")
    
    def test_simple_child_regeneration_determinism(self):
        state = State()
        actions = state.actions()
        children1 = []
        state.make(actions[0])
        children1.append(state.id())
        state.undo()
        state.make(actions[1])
        children1.append(state.id())
        state.undo()
        children2 = []
        state.make(actions[0])
        children2.append(state.id())
        state.undo()
        state.make(actions[1])
        children2.append(state.id())
        state.undo()
        self.assertEqual(children1, children2)

    def test_simple_child_regeneration_determinism_with_retain_graph(self):
        
        state = State(retain_graph=True)
        actions = state.actions()
        children1 = []
        state.make(actions[0])
        children1.append(state.id())
        state.undo()
        state.make(actions[1])
        children1.append(state.id())
        state.undo()
        children2 = []
        state.make(actions[0])
        children2.append(state.id())
        state.undo()
        state.make(actions[1])
        children2.append(state.id())
        state.undo()
        self.assertEqual(children1, children2)

    def test_compare_child_generation_with_unrelated_parameters(self):
       
        state1 = State()
        actions = state1.actions()
        children1 = []
        state1.make(actions[0])
        children1.append(state1.id())
        state1.undo()
        state1.make(actions[1])
        children1.append(state1.id())
        state2 = State(retain_graph=True)
        children2 = []
        state2.make(actions[0])
        children2.append(state2.id())
        state2.undo()
        state2.make(actions[1])
        children2.append(state2.id())
        state2.undo()
        self.assertEqual(children1, children2)


    def test_determinism_in_order_of_operations(self):
        def branching_function_Rand20(randint: RandomIntFunction, randf: RandomFloatFunction, params: StateParams) -> int:
            return randint(low=1, high=100)
        state1 = State(branching_function=branching_function_Rand20, seed=3)
        s1V = state1.value()
        state1.make(state1.actions()[0])
        state2 = State(branching_function=branching_function_Rand20, seed=3)
        state2.make(state2.actions()[0])
        s2V = state2.value()
        self.assertEqual(state1.id(), state2.id())
        self.assertEqual(s1V, s2V)
    
    def test_state_attribute_reproducability(self):
        """Tests whether state always produces the same attributes/values"""
        def s50_transposition_space_function(randint: RandomIntFunction, randf: RandomFloatFunction, globals: GlobalVariables, depth: int) -> int:
            return 50
        
        state_visit_count = dict()
        state_info = dict()
        def dfs(state: State, depth: int):
            if depth == 0:
                return
            state_str = state.id()
            visitCount = state_visit_count.get(state_str, 0)

            if visitCount == 0:
                val = state.value()
                hVal = state.heuristic_value()
                stateDepth = state.depth()
                isTerm = state.is_terminal()
                actions = state.actions()
                state_info[state_str] = {
                    "stateVal":val,
                    "stateHVal":hVal,
                    "stateDepth":stateDepth,
                    "isTerminal":isTerm,
                    "actions":actions,
                }
            elif visitCount == 1:
                val = state.value()
                hVal = state.heuristic_value()
                stateDepth = state.depth()
                isTerm = state.is_terminal()
                actions = state.actions()
                self.assertEqual(val, state_info[state_str]["stateVal"])
                self.assertEqual(hVal, state_info[state_str]["stateHVal"])
                self.assertEqual(stateDepth, state_info[state_str]["stateDepth"])
                self.assertEqual(isTerm, state_info[state_str]["isTerminal"])
                self.assertEqual(actions, state_info[state_str]["actions"])
            else:
                return

            state_visit_count[state_str] = visitCount + 1

            for action in state.actions():
                state.make(action)
                dfs(state, depth-1)
                state.undo()
        
        depth = 20
        state = State(transposition_space_function=s50_transposition_space_function)
        dfs(state, depth)


    def test_terminal_states_having_no_children(self):
        def branching_function_3(randint: RandomIntFunction, randf: RandomFloatFunction, params: StateParams) -> int:
            if params.self.depth > 3:
                if randf() > 0.1:
                    return 0  
            return 2
        
        def dfs(state: State):
            if state.is_terminal():
                self.assertEqual(len(state.actions()), 0)
                return
            for action in state.actions():
                state.make(action)
                dfs(state)
                state.undo()

        state = State(branching_function=branching_function_3)
        dfs(state)

    def test_different_graphs_based_on_seed(self):
        """Tests whether states with different seed produces different graphs"""
        state1 = State(seed=0)
        state1.make(state1.actions()[0])
        state2 = State(seed=1)
        state2.make(state2.actions()[0])
        self.assertNotEqual(state1.id(), state2.id())
        
        

if __name__ == '__main__':
    # unittest.main()
    TestState().test_different_graphs_based_on_seed()
