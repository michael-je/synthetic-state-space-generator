import unittest
import math
from typing import Any
from collections import defaultdict
import random

import sssg.RNGHasher as RNGHasher
from sssg.RNGHasher import RNGHasher as RNG
from sssg.SyntheticGraph import SyntheticGraph
from sssg.custom_types import *
from sssg.custom_exceptions import *
from sssg.constants import *
from sssg.utils import *

# pyright: reportPrivateUsage=false
# pyright: reportUnknownLambdaType=false
# pyright: reportMissingTypeStubs=false
# pyright: reportWildcardImportFromLibrary=false

random.seed(0)

class SeedGenerator():
    def __iter__(self):
        return self
    
    def __next__(self):
        return random.randint(0, 100000)

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
        """Test whether the RNG's results correctly follow the gaussian distribution when
        expected."""
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
        self.assertAlmostEqual(bins[ 0]/N_TRIALS, BAND_1, places=2)
        self.assertAlmostEqual(bins[ 1]/N_TRIALS, BAND_1, places=2)
        self.assertAlmostEqual(bins[ 2]/N_TRIALS, BAND_2, places=2)
        self.assertAlmostEqual(bins[ 3]/N_TRIALS, BAND_3, places=2)
    
    def test_uniform_distribution(self):
        """Test whether the RNG's results correctly follow the uniform distribution when
        expected."""
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


class TestSyntheticGraph(unittest.TestCase):
    
    def _walk_graph(self, state: SyntheticGraph, walk_seed: int=0):
        """Helper function to take a deterministic walk through the graph."""
        rng = RNG(distribution=RandomnessDistribution.UNIFORM, seed=walk_seed)
        while state.depth() < state.globals.vars.max_depth - 1:
            while rng.next_float() < 0.56 and not state.is_root():
                state.undo()
            while rng.next_float() < 0.6 and not state.is_terminal():
                state.make_random()

    def test_undo_root(self):
        state = SyntheticGraph()
        self.assertRaises(RootHasNoParent, lambda: state.undo())
        state.make(state.actions()[0])
        state.undo()
        self.assertRaises(RootHasNoParent, lambda: state.undo())
    
    def test_make_terminal(self):
        """An error should be raised when trying to use .make() on a terminal state."""
        state = SyntheticGraph()
        while not state.is_terminal():
            state.make(0)
        self.assertRaises(TerminalHasNoChildren, lambda: state.make(0))
    
    def test_depth(self):
        N_TRIALS = 100
        rng = RNGHasher.RNGHasher(RandomnessDistribution.UNIFORM)
        state = SyntheticGraph(max_depth=10000)
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
        self.assertEqual(state.depth(), depth,
            "Mismatch in depth returned by the state and the expected depth.")
    
    def test_state_parameter_ranges(self):
        self.assertRaises(ValueError, lambda: SyntheticGraph(seed=-1))
        self.assertRaises(ValueError, lambda: SyntheticGraph(seed=0xFFFFFFFF + 1))
        self.assertRaises(ValueError, lambda: SyntheticGraph(max_depth=-1))
        self.assertRaises(ValueError, lambda: SyntheticGraph(max_depth=0))
        self.assertRaises(ValueError, lambda: SyntheticGraph(max_depth=2**ID_BIT_LENGTH))
        self.assertRaises(ValueError, lambda: SyntheticGraph(max_depth=2**(ID_BIT_LENGTH - ID_TRUE_VALUE_BIT_LENGTH - ID_PLAYER_BIT_LENGTH)))
        self.assertRaises(ValueError, lambda: SyntheticGraph(root_true_value=-2))
        self.assertRaises(ValueError, lambda: SyntheticGraph(root_true_value=2))
        self.assertRaises(ValueError, lambda: SyntheticGraph(root_true_value=0.2)) # type: ignore
        self.assertRaises(ValueError, lambda: SyntheticGraph(branching_factor_base=-1))
        self.assertRaises(ValueError, lambda: SyntheticGraph(branching_factor_variance=-1))
        self.assertRaises(ValueError, lambda: SyntheticGraph(child_depth_minumum=2, child_depth_maximum=1))
        self.assertRaises(ValueError, lambda: SyntheticGraph(terminal_minimum_depth=-1))
        self.assertRaises(ValueError, lambda: SyntheticGraph(locality_grouping=-1))
        self.assertRaises(ValueError, lambda: SyntheticGraph(locality_grouping=1.5))
        self.assertRaises(ValueError, lambda: SyntheticGraph(true_value_forced_ratio=-1))
        self.assertRaises(ValueError, lambda: SyntheticGraph(true_value_forced_ratio=1.5))
        self.assertRaises(ValueError, lambda: SyntheticGraph(true_value_similarity_chance=-1))
        self.assertRaises(ValueError, lambda: SyntheticGraph(true_value_similarity_chance=1.5))
        self.assertRaises(ValueError, lambda: SyntheticGraph(true_value_tie_chance=-1))
        self.assertRaises(ValueError, lambda: SyntheticGraph(true_value_tie_chance=1.5))
        self.assertRaises(ValueError, lambda: SyntheticGraph(symmetry_factor=0))
        self.assertRaises(ValueError, lambda: SyntheticGraph(symmetry_factor=1.5))
        self.assertRaises(ValueError, lambda: SyntheticGraph(symmetry_frequency=-1))
        self.assertRaises(ValueError, lambda: SyntheticGraph(symmetry_frequency=1.5))
        self.assertRaises(ValueError, lambda: SyntheticGraph(heuristic_accuracy_base=-1))
        self.assertRaises(ValueError, lambda: SyntheticGraph(heuristic_accuracy_base=2))
        self.assertRaises(ValueError, lambda: SyntheticGraph(heuristic_depth_scaling=-1))
        self.assertRaises(ValueError, lambda: SyntheticGraph(heuristic_depth_scaling=2))
        self.assertRaises(ValueError, lambda: SyntheticGraph(heuristic_locality_scaling=-1))
        self.assertRaises(ValueError, lambda: SyntheticGraph(heuristic_locality_scaling=2))
    
    def test_basic_state_determinism_1(self):
        state1 = SyntheticGraph()
        self._walk_graph(state1)
        state1_id = state1.id()
        state2 = SyntheticGraph()
        self._walk_graph(state2)
        state2_id = state2.id()
        self.assertEqual(state1_id, state2_id)
    
    def test_basic_state_determinism_2(self):
        N_TRIALS = 50
        DEPTH = 30
        state1 = SyntheticGraph(max_depth=DEPTH)
        state2 = SyntheticGraph(max_depth=DEPTH)
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
        state = SyntheticGraph(max_depth=1)
        state.make_random()
    
    def test_maxdepth_error(self):
        state = SyntheticGraph(max_depth=1)
        state.make_random()
        self.assertRaises(TerminalHasNoChildren, lambda: state.make_random())
    
    def test_negative_branching_function(self):
        state = SyntheticGraph(branching_function=lambda *_: -1) # type: ignore
        self.assertRaises(TerminalHasNoChildren, lambda: state.make_random())
    
    def test_negative_child_depth(self):
        state = SyntheticGraph(child_depth_function=lambda *_: -1) # type: ignore
        self.assertRaises(IdOverflow, lambda: state.make_random())
    
    def test_large_child_depth(self):
        state = SyntheticGraph(max_depth=2, child_depth_function=lambda *_: 3) # type: ignore
        self.assertRaises(IdOverflow, lambda: state.make_random())
    
    def test_transposition_space_too_small(self):
        state = SyntheticGraph(transposition_space_function=lambda *_: 0) # type: ignore
        self.assertRaises(ValueError, lambda: state.make_random())
        state = SyntheticGraph(transposition_space_function=lambda *_: -1) # type: ignore
        self.assertRaises(ValueError, lambda: state.make_random())
    
    def test_transposition_space_barely_large_enough(self):
        state = SyntheticGraph(transposition_space_function=lambda *_: 1) # type: ignore
        state.make_random()

    def test_transposition_space_at_maximum(self):
        mtss = SyntheticGraph().globals.vars.max_transposition_space_size
        state = SyntheticGraph(transposition_space_function=lambda *_: mtss) # type: ignore
        state.make_random()
    
    def test_transposition_space_above_maximum(self):
        mtss = SyntheticGraph().globals.vars.max_transposition_space_size
        state = SyntheticGraph(transposition_space_function=lambda *_: mtss+1) # type: ignore
        self.assertRaises(IdOverflow, lambda: state.make_random())
    
    def test_id_bit_partitioning_1(self):
        """The bit partition of the transition space record should adapt to 
        the bit partition of the max depth."""
        OCCUPIED_BITS = ID_TRUE_VALUE_BIT_LENGTH + ID_PLAYER_BIT_LENGTH
        state = SyntheticGraph(max_depth=2**(ID_BIT_LENGTH - OCCUPIED_BITS -  1) - 1)
        self.assertEqual(2**1 -  1, state.globals.vars.max_transposition_space_size)
        state = SyntheticGraph(max_depth=2**(ID_BIT_LENGTH - OCCUPIED_BITS -  2) - 1)
        self.assertEqual(2**2 -  1, state.globals.vars.max_transposition_space_size)
        state = SyntheticGraph(max_depth=2**(ID_BIT_LENGTH - OCCUPIED_BITS - 32) - 1)
        self.assertEqual(2**32 - 1, state.globals.vars.max_transposition_space_size)
    
    def test_id_bit_partitioning_2(self):
        state1 = SyntheticGraph(max_depth=2**(ID_BIT_LENGTH-5))
        state2 = SyntheticGraph(max_depth=2**(ID_BIT_LENGTH-20))
        state3 = SyntheticGraph(max_depth=2**(ID_BIT_LENGTH-60))
        self.assertEqual(
            state1.globals.vars.max_depth * (state1.globals.vars.max_transposition_space_size + 1),
            state2.globals.vars.max_depth * (state2.globals.vars.max_transposition_space_size + 1))
        self.assertEqual( 
            state1.globals.vars.max_depth * (state1.globals.vars.max_transposition_space_size + 1),
            state3.globals.vars.max_depth * (state3.globals.vars.max_transposition_space_size + 1)
        )

    def test_transposition_space_size(self):
        T_SPACE_SIZES = [5, 10, 51, 100]
        for tspace_size in T_SPACE_SIZES:
            state = SyntheticGraph(
                transposition_space_function=lambda *args: tspace_size, # type: ignore
                branching_factor_base=10000)
            state.actions()
            unique_records = set(child.tspace_record for child in state._current.children)
            # should succeed with high probability
            self.assertEqual(tspace_size, len(unique_records),
                             f"There should be {tspace_size} unique records. unique_records: {unique_records}")
    
    def test_locality_1(self):
        """All transposition space records should be the same when locality=1"""
        state = SyntheticGraph(branching_factor_base=4, locality_grouping=1, max_depth=100)
        while not state.is_terminal():
            state.actions()
            child_records = [child.tspace_record for child in state._current.children]
            self.assertTrue(child_records[0] == child_records[1] == child_records[2] == child_records[3], 
                            f"All children should have the same tspace record. records: {child_records}")
            self.assertEqual(state._root.tspace_record, state._current.tspace_record,
                             "Children should have same tspace record as root.")
            state.make_random()
    
    def test_locality_0_distribution(self):
        """Transposition space records should be evenly spaced out accross the space when locality=0."""
        N_CHILDREN = 200000
        T_SPACE_SIZES = [5, 10, 51, 100]
        ERROR_MARGIN = 0.1
        for tspace_size in T_SPACE_SIZES:
            state = SyntheticGraph(
                branching_factor_base=N_CHILDREN,
                locality_grouping=0,
                transposition_space_function=lambda *args: tspace_size) # type: ignore
            state.actions()
            bins: defaultdict[int, int] = defaultdict(lambda: 0)
            for child in state._current.children:
                tspace_record = child.tspace_record
                bins[tspace_record] += 1
            expected_bin_size = N_CHILDREN / tspace_size
            for k in bins:
                self.assertLessEqual(abs(bins[k] - expected_bin_size), expected_bin_size * ERROR_MARGIN,
                                     f"Bin size exceeds the error margin. bins: {dict(bins)}")

    def test_locality_number_of_unique_records(self):
        """Unique transposition space records should only occupy a set range when locality != 0."""
        N_CHILDREN = 10000
        T_SPACE_SIZES = [5, 10, 51, 100]
        for tspace_size in T_SPACE_SIZES:
            for locality in [0.0, 0.25, 0.5, 0.75, 1.0]:
                state = SyntheticGraph(
                    branching_factor_base=N_CHILDREN,
                    locality_grouping=locality,
                    transposition_space_function=lambda *args: tspace_size) # type: ignore
                state.actions()
                unique_records = set(child.tspace_record for child in state._current.children)
                self.assertLessEqual(len(unique_records), math.ceil(tspace_size * (1-locality) + 1),
                                     f"Too many unique record ids ({len(unique_records)}) for given locality {locality} .")
    
    def test_transposition_space_locality_scaling(self):
        """Check whether locality bounds are correctly defined when transitioning between
        depth levels with different transposition space sizes."""
        N_CHILDREN = 10000
        LOCALITY = 0.5
        tspace_sizes = [50, 20, 100, 32, 3, 41, 325, 123, 52]
        state = SyntheticGraph(
            transposition_space_function=lambda *args: tspace_sizes[args[-1]], # type: ignore
            branching_factor_base=N_CHILDREN,
            locality_grouping=LOCALITY)
        for i in range(1, len(tspace_sizes)):
            parent_tspace_size, child_tspace_size = tspace_sizes[i-1], tspace_sizes[i]
            state.actions()
            unique_records = set(child.tspace_record for child in state._current.children)
            transposition_space_ratio = child_tspace_size / parent_tspace_size
            parent_record = state._current.tspace_record
            child_record_center = math.floor(parent_record * transposition_space_ratio)
            child_record_margin = (child_tspace_size-1) * (1-LOCALITY) / 2
            lower_variance_margin = math.floor(child_record_center - child_record_margin) % (child_tspace_size + 1)
            upper_variance_margin = math.floor(child_record_center + child_record_margin) % (child_tspace_size + 1)
            # should succeed with high probability
            self.assertIn(lower_variance_margin, unique_records,
                          "Lower locality margin of child tspace record should be included.")
            self.assertIn(upper_variance_margin, unique_records,
                          "Upper locality margin of child tspace record should be included.")
            self.assertNotIn(lower_variance_margin - 1, unique_records,
                             "Records outside of the locality margin should not be included.")
            self.assertNotIn(upper_variance_margin + 1, unique_records,
                             "Records outside of the locality margin should not be included.")
            state.make_random()

    def test_encode_id_0(self):
        """All bits of the id should be 0 if we pass in appropriate parameters."""
        state_node = SyntheticGraph()._current
        true_value = decode_true_value_bits(0)
        id = state_node._encode_id(true_value, Player(0), 0, 0)
        self.assertEqual(id, 0)
    
    def test_encode_id_all_to_1s(self):
        """All bit representations of values in the id should equal 1 if we pass
        in appropriate parameters."""
        state_node = SyntheticGraph()._current
        # create id
        true_value = decode_true_value_bits(1)
        id = state_node._encode_id(true_value, Player(1), 1, 1)
        bin_str = str(bin(id))[2:].zfill(HASH_OUTPUT_BIT_LENGTH - 1)
        # define margins
        id_true_value_offset = 0
        id_player_offset = ID_TRUE_VALUE_BIT_LENGTH
        id_depth_offset = id_player_offset + ID_PLAYER_BIT_LENGTH
        id_record_offset = id_depth_offset + state_node.globals.vars.max_depth.bit_length()
        # run assertions
        self.assertEqual(int(bin_str[id_true_value_offset:id_player_offset], 2), 1)
        self.assertEqual(int(bin_str[id_player_offset:id_depth_offset], 2), 1)
        self.assertEqual(int(bin_str[id_depth_offset:id_record_offset], 2), 1)
        self.assertEqual(int(bin_str[id_record_offset:],                2), 1)
    
    def test_encode_id_random(self):
        """Attributes encoded in the id should retain their correct value."""
        rng = SyntheticGraph()._RNG
        N_TRIALS = 100
        for _ in range(N_TRIALS):
            # define random values
            max_depth = rng.next_int(0, 2**32)
            state_node = SyntheticGraph(max_depth=max_depth)._current
            true_value = rng.next_int(-1, 1)
            player = Player(rng.next_int(0, 1))
            depth = rng.next_int(0, state_node.globals.vars.max_depth)
            tspace_record = rng.next_int(0, state_node.globals.vars.max_transposition_space_size)
            # create id
            id = state_node._encode_id(true_value, player, depth, tspace_record)
            bin_str = str(bin(id))[2:].zfill(HASH_OUTPUT_BIT_LENGTH - 1)
            # define margins
            id_value_offset = 0
            id_player_offset = ID_TRUE_VALUE_BIT_LENGTH
            id_depth_offset = id_player_offset + ID_PLAYER_BIT_LENGTH
            id_record_offset = id_depth_offset + state_node.globals.vars.max_depth.bit_length()
            # run assertions
            self.assertEqual(int(bin_str[id_value_offset:id_player_offset], 2), encode_true_value_to_bits(true_value))
            self.assertEqual(int(bin_str[id_player_offset:id_depth_offset], 2), player.value)
            self.assertEqual(int(bin_str[id_depth_offset:id_record_offset], 2), depth)
            self.assertEqual(int(bin_str[id_record_offset:],                2), tspace_record)
    
    def test_set_root(self):
        """Tests State.set_root(). Also inadvertently tests the extraction functions
        in utils.py."""
        state = SyntheticGraph()
        state.make(state.actions()[0])
        true_value = state.true_value()
        player = state.player()
        depth = state.depth()
        tspace_record = state._current.tspace_record
        state.set_root(state.id())
        self.assertEqual(state.true_value(), true_value)
        self.assertEqual(state.player(), player)
        self.assertEqual(state.depth(), depth)
        self.assertEqual(state._current.tspace_record, tspace_record)

    def test_simple_child_regeneration_determinism(self):
        state = SyntheticGraph()
        actions = state.actions()
        child_ids: list[int] = []
        state.make(actions[0])
        child_ids.append(state.id())
        state.undo()
        state.make(actions[1])
        child_ids.append(state.id())
        state.undo()
        child_ids: list[int] = []
        state.make(actions[0])
        child_ids.append(state.id())
        state.undo()
        state.make(actions[1])
        child_ids.append(state.id())
        state.undo()
        self.assertEqual(child_ids, child_ids)

    def test_compare_child_generation_with_unrelated_parameters(self):
        state1 = SyntheticGraph()
        actions = state1.actions()
        child_ids: list[int] = []
        state1.make(actions[0])
        child_ids.append(state1.id())
        state1.undo()
        state1.make(actions[1])
        child_ids.append(state1.id())
        state2 = SyntheticGraph()
        child_ids: list[int] = []
        state2.make(actions[0])
        child_ids.append(state2.id())
        state2.undo()
        state2.make(actions[1])
        child_ids.append(state2.id())
        state2.undo()
        self.assertEqual(child_ids, child_ids)
    
    def test_state_attribute_reproducability(self):
        """Tests whether state always produces the same attributes/values"""
        state_visit_count: defaultdict[int, int] = defaultdict(lambda: 0)
        state_info: dict[int, dict[str, int|float|bool|list[int]]] = dict()
        def dfs(state: SyntheticGraph):
            if state_visit_count[state.id()] == 0:
                state_info[state.id()] = {
                    "val": state.true_value(),
                    "hval": state.heuristic_value(),
                    "depth": state.depth(),
                    "terminal": state.is_terminal(),
                    "actions": state.actions(),
                }
            else:
                self.assertEqual(state.true_value(),      state_info[state.id()]["val"])
                self.assertEqual(state.heuristic_value(), state_info[state.id()]["hval"])
                self.assertEqual(state.depth(),           state_info[state.id()]["depth"])
                self.assertEqual(state.is_terminal(),     state_info[state.id()]["terminal"])
                self.assertEqual(state.actions(),         state_info[state.id()]["actions"])
            state_visit_count[state.id()] += 1
            for action in state.actions():
                state.make(action)
                dfs(state)
                state.undo()
        state = SyntheticGraph(
            max_depth=10, 
            transposition_space_function=lambda *args: 50) # type: ignore
        dfs(state)

    def test_different_graphs_based_on_seed(self):
        """Test whether states with different seed produces different graphs"""
        state1 = SyntheticGraph(seed=0)
        state1.make(state1.actions()[0])
        state2 = SyntheticGraph(seed=1)
        state2.make(state2.actions()[0])
        # should succeed with high probability
        self.assertNotEqual(state1.id(), state2.id())
    
    def test_determinism_in_order_of_operations(self):
        """Different orders of operations should not affect determinism."""
        def branching_function_1_to_100(randint: RandomIntFunction, randf: RandomFloatFunction, params: StateParams) -> int:
            return randint(low=1, high=100)
        rng = SyntheticGraph()._RNG
        state = SyntheticGraph(branching_function=branching_function_1_to_100, seed=3)
        state_funcs: list[Any] = [state.actions, state.depth, state.heuristic_value, state.id, state.is_root, state.is_terminal]
        N_TRIALS = 1000
        for _ in range(N_TRIALS):
            for _ in range(rng.next_int(0, 10)):
                state_funcs[rng.next_int(0, len(state_funcs) - 1)]()
            state.make(state.actions()[0])
            for _ in range(rng.next_int(0, 10)):
                state_funcs[rng.next_int(0, len(state_funcs) - 1)]()
            state1_id = state.id()
            state.undo()
            state._current.reset()
            for _ in range(rng.next_int(0, 10)):
                state_funcs[rng.next_int(0, len(state_funcs) - 1)]()
            state.make(state.actions()[0])
            for _ in range(rng.next_int(0, 10)):
                state_funcs[rng.next_int(0, len(state_funcs) - 1)]()
            state2_id = state.id()
            state.undo()
            self.assertEqual(state1_id, state2_id)
    
    def test_true_value_consistency_using_minimax(self):
        """Test whether the true values of the default graph behave as expected using
        a minimax search."""
        INF = 1000
        visited: dict[int, int] = {}
        def minimax(state: SyntheticGraph, depth: int) -> int:
            if state.id() in visited.keys():
                self.assertEqual(state.true_value(), visited[state.id()])
                return state.true_value()
            if state.is_terminal():
                return state.true_value()
            if depth == 0:
                return state.true_value()
            if state.player() == Player.MAX:
                max_eval = -INF
                for action in state.actions():
                    state.make(action)
                    s_eval = minimax(state, depth-1)
                    state.undo()
                    max_eval = max(max_eval, s_eval)
                visited[state.id()] = max_eval
                return max_eval
            else:
                min_eval = INF
                for action in state.actions():
                    state.make(action)
                    s_eval = minimax(state, depth-1)
                    state.undo()
                    min_eval = min(min_eval, s_eval)			
                visited[state.id()] = min_eval
                return min_eval
        N_TRIALS = 100
        for _ in range(N_TRIALS):
            state = SyntheticGraph(seed=next(seeds))
            true_value = minimax(state, 5)
            self.assertEqual(true_value, state.true_value())
            visited.clear()
        for _ in range(N_TRIALS):
            state = SyntheticGraph(seed=next(seeds), branching_factor_base=5)
            true_value = minimax(state, 3)
            self.assertEqual(true_value, state.true_value())
            visited.clear()
        
    def test_extreme_symmetry(self):
        bf = 1000
        state = SyntheticGraph(
            symmetry_factor=0.000001, symmetry_frequency=1.0, 
            branching_factor_base=bf)
        while not state.is_terminal():
            state.actions()
            children = state._current.children
            self.assertTrue(all([child == children[0] for child in children]))
            self.assertEqual(len(children), bf)
            state.make_random()
    
    def test_various_symmetry_values(self):
        bfunc = lambda randint, randf, params: randint(10, 1000) # type: ignore
        symmetries = [0.5, 0.25, 0.125]
        for symmetry_factor in symmetries:
            state = SyntheticGraph(
                symmetry_factor=symmetry_factor, symmetry_frequency=1,
                branching_function=bfunc) # type: ignore
            while not state.is_terminal():
                state.actions()
                self.assertEqual(
                    len(state._current.children), 
                    state._current.branching_factor(),
                    "There should be branching_factor number of children.")
                self.assertEqual(
                    len(set(child.id for child in state._current.children)), 
                    math.floor(state._current.branching_factor() * symmetry_factor),
                    "Incorrect number of unique children.")
                state.make_random()
    
    def test_very_low_true_value_forced_ratio(self):
        """"With a very low true_value_forced_ratio, and tie/similarity chances set to 0, 
        only one child should share a value with its parent."""
        N_TRIALS = 1000
        state = SyntheticGraph(
            true_value_forced_ratio=0.0001,
            true_value_similarity_chance=0,
            true_value_tie_chance=0,
            transposition_space_function=lambda *args: 100,  # type: ignore
            max_depth=7,
            branching_factor_base=7)
        rng = RNG(distribution=RandomnessDistribution.UNIFORM)
        for _ in range(N_TRIALS):
            if rng.next_float() < 0.8 and not state.is_terminal():
                state.make_random()
            elif not state.is_root():
                state.undo()
            if state.is_terminal():
                continue
            win: bool = (state.player() == Player.MAX and state.true_value() == 1) or \
                (state.player() == Player.MIN and state.true_value() == -1)
            draw: bool = True if state.true_value() == 0 else False
            parent_true_value = state.true_value()
            child_values: list[int] = []
            for action in state.actions():
                state.make(action)
                child_values.append(state.true_value())
                state.undo()
            if win or draw:
                self.assertEqual(child_values.count(parent_true_value), 1)

    def test_loss_true_value_forced(self):
        """"When in a loosing position, make sure that parents true value 
        is propogated to all children."""
        N_TRIALS = 1000
        state = SyntheticGraph(
            transposition_space_function=lambda *args: 100,  # type: ignore
            max_depth=7,
            branching_factor_base=7)
        rng = RNG(distribution=RandomnessDistribution.UNIFORM)
        for _ in range(N_TRIALS):
            if rng.next_float() < 0.8 and not state.is_terminal():
                state.make_random()
            elif not state.is_root():
                state.undo()
            if state.is_terminal():
                continue
            loss: bool = (state.player() == Player.MAX and state.true_value() == -1) or \
                (state.player() == Player.MIN and state.true_value() == 1)
            if not loss:
                continue
            parent_true_value = state.true_value()
            child_values: list[int] = []
            for action in state.actions():
                state.make(action)
                child_values.append(state.true_value())
                state.undo()
            self.assertEqual(child_values.count(parent_true_value), len(child_values))

    def test_set_root_determinism(self):
        """Testing whether set_root() breaks determinism. This test traverses the whole graph
        and collects information about all states while also randomly picking some states 
        for sampling. For each sampled state s, we call set_root(s) and traverse the graph 
        again to make sure that the revisited states produce the same attributes."""
        def child_depth_function_cycles_allowed(randint: RandomIntFunction, randf: RandomFloatFunction, params: StateParams) -> int:
            if randf() < 0.1:
                return abs(params.self.depth - 3)
            else:
                return params.self.depth + 1
        state = SyntheticGraph(
            transposition_space_function=lambda *args: 100, # type: ignore
            child_depth_function=child_depth_function_cycles_allowed,
            branching_factor_base=10,
            max_depth=5)
        rng_test = RNG(RandomnessDistribution.UNIFORM)
        state_info_from_root: dict[int, dict[str, int|float|bool]] = dict()
        set_root_tests: list[int] = []
        #Search from original state/root
        def dfs_from_original_root(state: SyntheticGraph):
            if state.id() in state_info_from_root:
                return
            state_info_from_root[state.id()] = {
                    "val": state.true_value(),
                    "hval": state.heuristic_value(),
                    "depth": state.depth(),
                    "terminal": state.is_terminal(),
                    "child_count": len(state.actions())
                }
            if state.is_terminal():
                return
            elif rng_test.next_float() < 0.00025:
                set_root_tests.append(state.id()) #randomly sample state
            for action in state.actions():
                state.make(action)
                dfs_from_original_root(state)
                state.undo()
            return
        visited: set[int] = set()
        def dfs_from_new_root(state: SyntheticGraph):
            if state.id() in visited:
                return
            #Testing reproducability
            self.assertIn(state.id(),                 state_info_from_root)
            self.assertEqual(state.true_value(),      state_info_from_root[state.id()]["val"])
            self.assertEqual(state.heuristic_value(), state_info_from_root[state.id()]["hval"])
            self.assertEqual(state.depth(),           state_info_from_root[state.id()]["depth"])
            self.assertEqual(state.is_terminal(),     state_info_from_root[state.id()]["terminal"])
            self.assertEqual(len(state.actions()),    state_info_from_root[state.id()]["child_count"])
            if state.is_terminal():
                return
            visited.add(state.id())
            for action in state.actions():
                state.make(action)
                dfs_from_new_root(state)
                state.undo()
        #call dfs from root
        dfs_from_original_root(state)
        for sampled_id in set_root_tests:
            visited = set()
            state.set_root(sampled_id)
            dfs_from_new_root(state)

    def test_set_terminal_root(self):
        """Take random walk until we reach terminal node, set it as root 
        and make sure that we can't make any moves or undo. 
        """
        state = SyntheticGraph(max_depth=5)
        while not state.is_terminal():
            state.make_random()
        state.set_root(state.id())
        self.assertRaises(TerminalHasNoChildren, lambda: state.make_random())
        self.assertRaises(RootHasNoParent, lambda: state.undo())
    
    def test_terminal_depth(self):
        TERMINAL_MINIMUM_DEPTH = 10
        state = SyntheticGraph(
            max_depth=20,
            terminal_minimum_depth=TERMINAL_MINIMUM_DEPTH,
            branching_factor_base=0)
        for _ in range(TERMINAL_MINIMUM_DEPTH):
            state.make_random()
        self.assertRaises(TerminalHasNoChildren, lambda: state.make_random())
    
    def test_terminal_chance(self):
        MAX_DEPTH = 10000
        state1 = SyntheticGraph(
            max_depth=MAX_DEPTH,
            terminal_chance=0
        )
        for _ in range(MAX_DEPTH-1):
            state1.make_random()
        state2 = SyntheticGraph(
            max_depth=MAX_DEPTH,
            terminal_chance=1,
            terminal_minimum_depth=0,
        )
        self.assertRaises(TerminalHasNoChildren, lambda: state2.make_random())


if __name__ == '__main__':
    unittest.main()
