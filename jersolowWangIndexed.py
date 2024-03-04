def jersolow_wang_2_sided_method2(cnf):
    literal_weight = defaultdict(int)
    for clause in cnf:
        for index, literal in enumerate(clause, start=1):
            if literal == 1:
                literal_weight[index] += 2 ** -len(clause)
            elif literal == 2:
                literal_weight[-index] += 2 ** -len(clause)
            # For 0, indicating the variable doesn't appear in the clause
            elif literal == 0:
                pass
            # Add more conditions if needed for other values
    return max(literal_weight, key=literal_weight.get)+1
