import multiprocessing
from collections import defaultdict

def calculate_literal_weight(clause):
    literal_weight = defaultdict(int)
    for index, value in enumerate(clause):
        if value != 0:  # Ignore variables that don't appear in the clause
            weight = 2 ** -sum(1 for v in clause if v != 0)  # Weight is 2^-size of clause
            literal_weight[index + 1 if value == 1 else -index - 1] += weight
    return literal_weight

def jersolow_wang_2_sided_method(cnf_index):
    pool = multiprocessing.Pool()
    results = pool.map(calculate_literal_weight, cnf_index)
    pool.close()
    pool.join()
    
    literal_weight = defaultdict(int)
    for result in results:
        for literal, weight in result.items():
            literal_weight[literal] += weight
                
    return max(literal_weight, key=literal_weight.get)

if __name__ == "__main__":
    cnf_index = [[1,0,1,2],[0,0,0,1],[0,1,2,0]]
    result = jersolow_wang_2_sided_method(cnf_index)
    print("Variable selected:", result)
