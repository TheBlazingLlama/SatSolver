#Code for testing logic.
import string
from collections import defaultdict
import copy
import multiprocessing

# Return the input line except delimited by spaces
def get_new_line_parsed():
    line = input()
    parsed_line = line.split(" ")
    return parsed_line

# Check if the parsed line is a comment
def is_comment(line):
    if line[0] == "c":
        return 1
    return 0

# Check if the parsed line is a preamble
def is_preamble(line):
    if line[0] == "p":
        return 1
    return 0

# Generate the cube list
def generate_cnf():
    num_vars = 0
    num_minterms = 0
    line = get_new_line_parsed()
    while is_comment(line):
        line = get_new_line_parsed()

    if is_preamble(line):
        cnf = []
        num_vars = int(line[2])
        num_minterms = int(line[3])
        for i in range(num_minterms):
            eqn_line = get_new_line_parsed()
            cube = generate_cube(eqn_line, num_vars)
            cnf.append(cube)

    return num_minterms, num_vars, cnf

# Generate a cube based off a given parsed line.
def generate_cube(line, num_var):
    cube = [0] * num_var
    
    for var in line:
        var = int(var)
        if var == 0:
            continue
        elif var > 0:
            cube[abs(var) - 1] = 1
        else:
            cube[abs(var) - 1] = 2

    return cube

def create_clause_set(num_minterms, num_vars):
    set_of_clauses = []

    for i in range(num_minterms):
        set_of_clauses.append([0])
        for j in range(num_vars-1):
            set_of_clauses[i].append(0)

    return set_of_clauses

# Returns varible to split on. When calling backtrack method call as such - backtrack(cnf, jersolow_wang(cnf))
# If no solution from that then try - backtrack(cnf, -jersolow_wang(cnf)) to negate 
# Approx 50% speed increase from standard jersolow wang
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


def process_clause(clause, unit, flag, modified, lock):
    if clause[unit-1] == 1:
        if flag == 2:
              clause[unit] = 0
              new_clause = clause
              if not new_clause:
                return -1
              modified.append(new_clause)
        elif flag == 1:
            return
    if clause[unit-1] == 2:
        if flag==1:
            clause[unit-1] = 0
            new_clause = clause
            if not new_clause:
                with lock:
                    modified.append(-1)
                return
            with lock:
                modified.append(new_clause)
        elif flag==2:
            return
    else:
        with lock:
            modified.append(clause)

def bcp(cnf, unit, flag):
    modified = multiprocessing.Manager().list()  # Shared list for storing modified clauses
    lock = multiprocessing.Lock()  # Lock to ensure process-safe access to the shared list
    
    # Create processes for each clause
    processes = []
    for clause in cnf:
        process = multiprocessing.Process(target=process_clause, args=(clause, unit, flag, modified, lock))
        process.start()
        processes.append(process)
    
    # Wait for all processes to finish
    for process in processes:
        process.join()
    
    return list(modified)
def if_one_literal(clause):
    count_one = 0
    #print(clause)
    for literal in clause:
        if literal != 0:
            count_one += 1
    if count_one == 1:
        return 1
    return 0
    
def unit_index(clause):
  index = 0;
  for literal in clause:
        index += 1 
        if literal != 0:
            break
  return index-1
  
def unit_polarity(clause, index):
  polarity = 0
  if clause[index] == 1:
    return 1
  elif clause[index] == 2:
    return 2

    
# Perform unit propagation. Standard across most DPLL implementations seen.
def unit_propagation(cnf):
    row = 0
    polarity = 0
    assignment = []
    unit_clauses = []
    
    for clause in cnf:
      if if_one_literal(clause)==1:
        unit_clauses.append(clause)
        row += 1
        
    while unit_clauses:
        print(f'cnf before bcp (unit prop): {cnf}')
        print(f'unit_clause: {unit_clauses}')
        unit = unit_clauses[0]
        print(f'unit: {unit}')
        index = unit_index(unit)
        print(f'index: {index}')
        polarity = unit_polarity(unit, index)
        print(f'polarity: {polarity}')
        cnf = bcp(cnf, index, polarity)
        assignment += [unit]
        print(f'cnf after bcp (unit prop): {cnf}')
        print(f'row: {row}')
        if clauses_unsat(cnf): #cnf == -1:
            return -1, [], row
        if clauses_all_one(cnf):#not cnf:
            print('hi :)')
            return cnf, assignment, row
        unit_clauses = []
        for clause in cnf:
          if if_one_literal(clause)==1:
            unit_clauses.append(clause)
            row += 1
    return cnf, assignment, row

# Check if all clauses evaluate to 1 (if set of clauses is empty)
def clauses_all_one(set_of_clauses):

    if len(set_of_clauses) == 0:
        return 1
    else:
        return 0
    
def all_dc(clause):
    try:
        for val in clause:
            if val != clause[0]:
                return 0
        return 1
    except:
        if clause == 0:
            return 1
    return 0

# Check if any clause evaluates to 0
def clauses_unsat(set_of_clauses):

    for clause in set_of_clauses:
        unsat = 1
        if(all_dc(clause)):
            unsat = 0
        else:
            for value in clause:
                if value == 1:                            
                    unsat = 0

        if unsat:
            return 1

    return 0

def dpll(cnf, set_of_clauses):
    
    # Call Unit Proagation to perform BCP.
    cnf, unit_assignment, row = unit_propagation(cnf)
    print(f'cnf: {cnf}')
    print(f'unit_assignment: {unit_assignment}')
    if unit_assignment:
      set_of_clauses[row] = unit_assignment[0]
    print(f'soc: {set_of_clauses}')
    # If the clauses all simplify to 1
    if clauses_all_one(cnf):
        # Return SAT
        return 1
    # If set contains a clause that evalulates to 0
    if clauses_unsat(cnf):
        # Return UNSAT
        return set_of_clauses
    
    # Recursively call dpll to test different variables. Acts as the recursive part of the DPLL algorithm.
    
    variable = jersolow_wang_2_sided_method(cnf)
    print(f'variable: {variable}')
    # pool.multiprocessing.Pool()
    # pool.multiprocessing.Pool(processes=2)
    
    set_of_clauses[variable-1] = 1
    solution = dpll(bcp(cnf, variable-1, 1), set_of_clauses)
    if not solution:
        set_of_clause[variable-1] = 2
        solution = dpll(bcp(cnf, variable-1, 2), set_of_clauses)
    return solution


if __name__ == "__main__":
    num_minterms, num_vars, cnf = generate_cnf()
    set_of_clauses = create_clause_set(num_minterms,num_vars)

    print(cnf)
    print(set_of_clauses)

    # perform calculation
    if dpll(cnf, set_of_clauses):
        print("SAT")
    else:
        print("UNSAT")
