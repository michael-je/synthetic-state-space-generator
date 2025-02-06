from State import State
import tests


def main():
    tests.test_hash_average(100000)
    tests.test_undo()
    tests.test_deterministic(3, 20)
        

main()
