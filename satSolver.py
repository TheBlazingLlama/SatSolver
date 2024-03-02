import string
from collections import defaultdict
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
    cube = [None] * num_var
    
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
        set_of_clauses.append([None])
        for j in range(num_vars-1):
            set_of_clauses[i].append(None)

    return set_of_clauses

# Returns varible to split on. When calling backtrack method call as such - backtrack(cnf, jersolow_wang(cnf))
# If no solution from that then try - backtrack(cnf, -jersolow_wang(cnf)) to negate 
# Approx 50% speed increase from standard jersolow wang
def jersolow_wang_2_sided_method(cnf):
  literal_weight = defaultdict(int)
  for clause in cnf:
    for literal in clause:
      literal_weight[abs(literal)] += 2 ** -len(clause)
  return max(literal_weight, key=literal_weight.get)

# Somewhat standard among most DPLL implementations, input is cnf and the splitting variable, output is new cnf
def bcp(cnf, unit):
    modified = []
    for clause in cnf:
        if unit in clause:
            continue
        if -unit in clause:
            new_clause = [x for x in clause if x != -unit]
            if not new_clause:
                return -1
            modified.append(new_clause)
        else:
            modified.append(clause)
    return modified
    
# Perform unit propagation. Standard across most DPLL implementations seen.
def unit_propagation(cnf):
    assignment = []
    unit_clauses = [clause for clause in cnf if len(clause) == 1]
    while unit_clauses:
        unit = unit_clauses[0]
        cnf = bcp(clause, unit[0])
        assignment += [unit[0]]
        if cnf == -1:
            return -1, []
        if not cnf:
            return cnf, assignment
        unit_clauses = [clause for clause in cnf if len(clause) == 1]
    return cnf, assignment

# Check if all clauses evaluate to 1 (if set of clauses is empty)
def clauses_all_one(set_of_clauses):

    if len(set_of_clauses) == 0:
        return True
    else:
        return False

# Check if any clause evaluates to 0
def clauses_unsat(set_of_clauses):

    for clause in set_of_clauses:
        unsat = True
        for value in clause:
            if value == 1:
                unsat = False

        if unsat:
            return True

    return False

def dpll(cnf, set_of_clauses):
    
    # Call Unit Proagation to perform BCP.
    cnf, unit_assignment = unit_propagation(cnf)
    set_of_clauses = set_of_clauses + unit_assignment

    # If the clauses all simplify to 1
    if clauses_all_one(set_of_clauses):
        # Return SAT
        return True
    # If set contains a clause that evalulates to 0
    if clauses_unsat(set_of_clauses):
        # Return UNSAT
        return False
    
    # Recursively call dpll to test different variables. Acts as the recursive part of the DPLL algorithm.
    
    variable = jeroslow_wang_2_sided_method(cnf)
    
    #pool.multiprocessing.Pool()
    #pool.multiprocessing.Pool(processes=2)
    
    solution = dpll(bcp(cnf, variable), set_of_clauses + [variable])
    if not solution:
        solution = dpll(bcp(cnf, -variable), set_of_clauses + [-variable])


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
