from collections import defaultdict
import multiprocessing

def calculate_literal_weight(clause, literal_weight, lock):
    """
    Function to calculate weights for each literal within a clause.
    """
    for i, presence in enumerate(clause, start=1):
        if presence == 1:
            with lock:
                literal_weight[i] += 2 ** -len(clause)
        elif presence == 2:
            with lock:
                literal_weight[-i] += 2 ** -len(clause)

def jeroslow_wang_2_sided_method_parallel(cnf):
    """
    Function to apply the Jeroslow-Wang 2-sided method in parallel.
    """
    literal_weight = multiprocessing.Array('d', [0.0] * (len(cnf[0]) + 1))  # Array for storing literal weights
    lock = multiprocessing.Lock()  # Lock to ensure process-safe access to the shared array
    
    # Create processes for calculating weights for each clause
    processes = []
    for clause in cnf:
        process = multiprocessing.Process(target=calculate_literal_weight, args=(clause, literal_weight, lock))
        process.start()
        processes.append(process)
    
    # Wait for all processes to finish
    for process in processes:
        process.join()
    
    # Find the literal with the maximum weight
    max_literal = max(range(1, len(literal_weight)), key=lambda i: literal_weight[i])
    
    return max_literal

if __name__ == '__main__':
    # Example usage:
    cnf = [[1, 1, 2], [2, 0, 1], [0, 1, 1]]
    result = jeroslow_wang_2_sided_method_parallel(cnf)
    print("Literal with maximum weight:", result)
