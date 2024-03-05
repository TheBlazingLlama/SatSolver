import multiprocessing

# Function to process each clause
def process_clause(clause, unit, modified, lock):
    if clause[unit-1] == 1:
        return
    if clause[unit-1] == 2:
        clause[unit-1] = 0
        new_clause = clause
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
    cnf = [[1, 0, 1, 2], [0, 0, 0, 1], [1, 1, 2, 0]]
    unit = 1
    result = bcp_parallel(cnf, unit)
    print(result)
