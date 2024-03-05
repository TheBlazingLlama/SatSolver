import multiprocessing
from collections import defaultdict

def jersolow_wang_worker(chunk_cnf, result_queue):
    literal_weight = defaultdict(int)
    for clause in chunk_cnf:
        for literal in clause:
            literal_weight[abs(literal)] += 2 ** -len(clause)
    result_queue.put(literal_weight)

def jersolow_wang_2_sided_method_parallel(cnf):
    num_processes = multiprocessing.cpu_count()
    chunk_size = len(cnf) // num_processes
    manager = multiprocessing.Manager()
    result_queue = manager.Queue()
    processes = []

    for i in range(num_processes):
        start_idx = i * chunk_size
        end_idx = start_idx + chunk_size if i < num_processes - 1 else len(cnf)
        chunk_cnf = cnf[start_idx:end_idx]
        p = multiprocessing.Process(target=jersolow_wang_worker, args=(chunk_cnf, result_queue))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    combined_literal_weight = defaultdict(int)
    while not result_queue.empty():
        literal_weight = result_queue.get()
        for literal, weight in literal_weight.items():
            combined_literal_weight[literal] += weight

    return max(combined_literal_weight, key=combined_literal_weight.get)

#this one is for testing the parallel
def jersolow_wang_2_sided_method(cnf):
  literal_weight = defaultdict(int)
  for clause in cnf:
    for literal in clause:
      literal_weight[abs(literal)] += 2 ** -len(clause)
  return max(literal_weight, key=literal_weight.get)

if __name__ == "__main__":
    cnf_index = [[1,2,4], [-1, -2, 4], [ 5], [-3, -5]]
    result = jersolow_wang_2_sided_method_parallel(cnf_index)
    print("Variable selected:", result)
    result = jersolow_wang_2_sided_method(cnf_index)
    print("Variable selected:", result)
