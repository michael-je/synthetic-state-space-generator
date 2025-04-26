import tests
import random


def main():
    # tests.test_hash_average(1000000)
    # tests.test_deterministic_graph_2()
    # tests.test_random_graph()
    # tests.test_ids()
    tests.test_gaussian_float_distribution(n_trials=10000, decimal_accuracy=2, seed=random.randint(0, 1000000))
    tests.test_gaussian_int_distribution(n_trials=10000, dist_range=100, seed=random.randint(0, 1000000))
        

main()
