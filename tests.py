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

    def _walk_graph(self, state: State, walk_seed: int=0):
        rng = RNG(distribution=RandomnessDistribution.UNIFORM, seed=walk_seed)
        while state.depth() < state.globals.vars.max_depth - 1:
            while rng.next_float() < 0.56 and not state.is_root():
                state.undo()
            while rng.next_float() < 0.6 and not state.is_terminal():
                state.make_random()
    
    # def _default_test_states(self):
    #     return [
    #         State(max_depth=0),
    #         State(max_depth=1),
    #         State(max_depth=10000),
    #         State(branching_factor_base=10, max_depth=100),
    #     ]

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
        self.assertEqual(state.depth(), depth)
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
        self.assertRaises(ValueError, lambda: State(max_depth=2**ID_BITS_SIZE))
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
    
    def test_negative_branching_function(self):
        state = State(branching_function=lambda *args: -1) # type: ignore
        self.assertRaises(TerminalHasNoChildren, lambda: state.make_random())
    
    def test_negative_child_depth(self):
        state = State(child_depth_function=lambda *args: -1) # type: ignore
        self.assertRaises(IdOverflow, lambda: state.make_random())
    
    def test_large_child_depth(self):
        state = State(max_depth=2, child_depth_function=lambda *args: 3) # type: ignore
        self.assertRaises(IdOverflow, lambda: state.make_random())
    
    # def test_maxdepth_1(self):
    #     state = State(max_depth=1)
    #     state.make_random()



if __name__ == '__main__':
    unittest.main()
