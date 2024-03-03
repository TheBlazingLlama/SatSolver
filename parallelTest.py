import multiprocessing

# Function to process each clause
def process_clause(clause, unit, modified, lock):
    if unit in clause:
        return
    if -unit in clause:
        new_clause = [x for x in clause if x != -unit]
        if not new_clause:
            with lock:
                modified.append(-1)
            return
        with lock:
            modified.append(new_clause)
    else:
        with lock:
            modified.append(clause)

def bcp_parallel(cnf, unit):
    modified = multiprocessing.Manager().list()  # Shared list for storing modified clauses
    lock = multiprocessing.Lock()  # Lock to ensure process-safe access to the shared list
    
    # Create processes for each clause
    processes = []
    for clause in cnf:
        process = multiprocessing.Process(target=process_clause, args=(clause, unit, modified, lock))
        process.start()
        processes.append(process)
    
    # Wait for all processes to finish
    for process in processes:
        process.join()
    
    return list(modified)

if __name__ == '__main__':
    # Example usage:
    cnf = [[1, 3, -4], [4], [2, -3, 1]]
    unit = 4
    result = bcp_parallel(cnf, unit)
    print(result)
