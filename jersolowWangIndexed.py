def jersolow_wang_2_sided_method2(cnf_index):
    literal_weight = defaultdict(int)
    
    for clause in cnf_index:
        for index, value in enumerate(clause):
            if value != 0:  # Ignore variables that don't appear in the clause
                weight = 2 ** -sum(1 for v in clause if v != 0)  # Weight is 2^-size of clause
                literal_weight[index + 1 if value == 1 else -index - 1] += weight
                
    return max(literal_weight, key=literal_weight.get)
