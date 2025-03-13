import tests


def main():
    # tests.test_hash_average(1000000)
    # tests.test_undo()
    # tests.test_deterministic(3, 20)
    
    tests.test_deterministic_graph()
    # tests.test_deterministic_graph(retain_tree=False)
    # tests.test_random_graph()
    # tests.test_random_graph(retain_tree=False)
        

main()
