import multiprocessing

def bcp(chunk_cnf, unit, flag, result_queue):
    new_cnf = []
    if flag == 1:
        unit_literal = unit
        neg_unit_literal = -unit
    elif flag == 2:
        unit_literal = -unit
        neg_unit_literal = unit
        
    for clause in chunk_cnf:
        if unit_literal in clause:
            continue
        if neg_unit_literal in clause:
            new_clause = [literal for literal in clause if literal != neg_unit_literal]
            if not new_clause:
                result_queue.put(-1)
                return
            new_cnf.append(new_clause)
        else:
            new_cnf.append(clause)
    result_queue.put(new_cnf)
# use 1 for flag if positive and 2 if complemented
def parallel_bcp(cnf, unit, flag):
    processes = []
    num_processes = multiprocessing.cpu_count()
    chunk_size = len(cnf) // num_processes
    manager = multiprocessing.Manager()
    result_queue = manager.Queue()
    
    for i in range(num_processes):
        start_idx = i * chunk_size
        end_idx = start_idx + chunk_size if i < num_processes - 1 else len(cnf)
        chunk_cnf = cnf[start_idx:end_idx]
        p = multiprocessing.Process(target=bcp, args=(chunk_cnf, unit, flag, result_queue))
        processes.append(p)
        p.start()
    
    for p in processes:
        p.join()
    
    new_cnf = []
    while not result_queue.empty():
        result = result_queue.get()
        if result == -1:
            return -1
        else:
            new_cnf.extend(result)
    
    return new_cnf

if __name__ == "__main__":
    cnf = [[1, 2, 3], [-1, -2, 4], [3, 5], [-3, -5]]
    unit = 3
    flag = 1
    new_cnf = parallel_bcp(cnf, unit, flag)
    print(new_cnf)
