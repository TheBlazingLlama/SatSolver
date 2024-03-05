from satSolverParallel import *
import copy

def jersolow_wang_2_sided_method(cnf):
    literal_weight = defaultdict(int)
    for clause in cnf:
        for literal in clause:
            literal_weight[abs(literal)] += 2** -len(clause)
    return max(literal_weight, key=literal_weight.get)

def bcp(cnf, unit, flag):
    new_cnf = []
    if flag == 1:
        unit_literal = unit
        neg_unit_literal = -unit
    elif flag == 2:
        unit_literal = -unit
        neg_unit_literal = unit
        
    for clause in cnf:
        if unit_literal in clause:
            continue
        if neg_unit_literal in clause:
            new_clause = [literal for literal in clause if literal != neg_unit_literal]
            if not new_clause:
                continue
            new_cnf.append(new_clause)
        else:
            new_cnf.append(clause)
    return new_cnf

# Perform unit propagation. Standard across most DPLL implementations seen.
def unit_propagation(cnf):
    row = 0
    assignment = []
    unit_clauses = []

    for clause in cnf:
        if len(clause) == 1:
            unit_clauses.append(clause)
    
    for clause in cnf:
      if if_one_literal(clause)==1:
        unit_clauses.append(clause)
        
    while unit_clauses:
        literal = unit_clauses[0]
        index = literal[0]
        cnf = bcp(cnf, index, 1)
        assignment += [literal]
        if clauses_unsat(cnf): #cnf == -1:
            return -1, []
        if clauses_all_one(cnf):#not cnf:
            return cnf, assignment
        unit_clauses = []
        for clause in cnf:
          if len(clause)==1:
            unit_clauses.append(clause)
    return cnf, assignment

def dpll(cnf, set_of_clauses):
    
    # Call Unit Proagation to perform BCP.
    cnf, unit_assignment = unit_propagation(cnf)
    set_of_clauses.append(unit_assignment)

    #print(f'cnf: {cnf}')
    #print(f'unit_assignment: {unit_assignment}')
    #print(f'soc: {set_of_clauses}')

    # If the clauses all simplify to 1
    if clauses_all_one(cnf):
        # Return SAT
        return set_of_clauses
    # If set contains a clause that evalulates to 0
    if clauses_unsat(cnf):
        # Return UNSAT
        return 0
    
    # Recursively call dpll to test different variables. Acts as the recursive part of the DPLL algorithm.
    
    variable = jersolow_wang_2_sided_method(cnf)
    
    # pool.multiprocessing.Pool()
    # pool.multiprocessing.Pool(processes=2)
    # Doesn't work
    solution = dpll(bcp(cnf, variable, 1), set_of_clauses + [variable])
    if not solution:
        solution = dpll(bcp(cnf, variable, 2), set_of_clauses + [-variable])
    return solution

if __name__ == "__main__":
    num_minterms, num_vars, parallel_cnf = generate_cnf_value_based()
    single_cnf = copy.deepcopy(parallel_cnf)
    set_of_clauses = create_clause_set(num_minterms,num_vars)

    #print(cnf)
    # print(set_of_clauses)

    # perform calculation
    '''
    print("Parallel Calculation:")
    start_time = time.time()
    result = dpll_parallel(parallel_cnf, set_of_clauses)
    if result:
        print("SATISFIABLE")
        print_nested_clauses(result)
        print()
    else:
        print("UNSATISFIABLE")

    end_time = time.time()
    

    elapsed_time = end_time - start_time
    print("Elapsed time:", elapsed_time, "seconds")
    '''
    set_of_clauses = create_clause_set(num_minterms,num_vars)
    print("Single Thread Calculation:")


    start_time = time.time()
    result = dpll(single_cnf, set_of_clauses)
    if result:
        print("SATISFIABLE")
        print_nested_clauses(result)
        print()
    else:
        print("UNSATISFIABLE")

    end_time = time.time()

    elapsed_time = end_time - start_time
    print("Elapsed time:", elapsed_time, "seconds")