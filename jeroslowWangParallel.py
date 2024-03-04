from collections import defaultdict
from multiprocessing import Pool, cpu_count

def process_clause(clause):
    local_weight = defaultdict(int)
    for index, literal in enumerate(clause, start=1):
        if literal == 1:
            local_weight[index] += 2 ** -len(clause)
        elif literal == 2:
            local_weight[-index] += 2 ** -len(clause)
        # For 0, indicating the variable doesn't appear in the clause
        elif literal == 0:
            pass
        # Add more conditions if needed for other values
    return local_weight

def merge_dicts(dict_list):
    merged_dict = defaultdict(int)
    for d in dict_list:
        for key, value in d.items():
            merged_dict[key] += value
    return merged_dict

def jersolow_wang_p(cnf):
    with Pool(cpu_count()) as pool:
        results = pool.map(process_clause, cnf)
    merged_result = merge_dicts(results)
    return max(merged_result, key=merged_result.get) 

if __name__ == '__main__':
    # Example usage:
    cnf1 = [[2, 1, 1, 2], [2, 0, 1, 1], [1, 1, 0, 1], [0, 0, 0, 1], [0, 2, 0, 1]]
    res = jersolow_wang_p(cnf1)
    print("Literal with maximum weight parallel:", res)
