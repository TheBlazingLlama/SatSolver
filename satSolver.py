import string
from collections import defaultdict
import multiprocessing

# Return the input line except delimited by spaces
def get_lines_cleaned(file_name):
    lines = []
    file = open(file_name)
    for line in file:
        split_line = line.split(" ")
        
        for i in range(len(split_line)):
            split_line[i] = split_line[i].rstrip()
            split_line[i] = split_line[i].rstrip("%")

        while "" in split_line: 
            split_line.remove("")

        if not split_line: 
            continue

        lines.append(split_line)
    return lines

# Check if the parsed line is a comment
def is_comment(line):
    if "c" in line:
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
    file_name = input("Input the file you would like to read from: ")
    lines = get_lines_cleaned(file_name)
    cnf = []
    for line in lines:
        if is_comment(line):
            continue
        if is_preamble(line):
            num_vars = int(line[2])
            num_minterms = int(line[3])
        else:
            cube = generate_cube(line, num_vars)
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

def if_one_literal(clause):
    count_one = 0
    count_two = 0
    for literal in clause:
        if literal == 1:
            count_one += 1
        if literal == 2:
            count_two += 1
    if count_two > 0:
        return 0
    if count_one == 1:
        return 1
    return 0
    
# Perform unit propagation. Standard across most DPLL implementations seen.
def unit_propagation(cnf):
    assignment = []
    unit_clauses = [clause for clause in cnf if if_one_literal(clause) == 1]
    print(unit_clauses)
    while unit_clauses:
        unit = unit_clauses[0]
        cnf = bcp(cnf, unit[0])
        print(cnf)
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
    cnf, unit_assignment = unit_propagation(cnf)
    set_of_clauses = set_of_clauses + unit_assignment
    print(set_of_clauses)
    # If the clauses all simplify to 1
    if clauses_all_one(set_of_clauses):
        # Return SAT
        return 1
    # If set contains a clause that evalulates to 0
    if clauses_unsat(set_of_clauses):
        # Return UNSAT
        return 0
    
    # Recursively call dpll to test different variables. Acts as the recursive part of the DPLL algorithm.
    
    variable = jersolow_wang_2_sided_method(cnf)
    
    # pool.multiprocessing.Pool()
    # pool.multiprocessing.Pool(processes=2)
    
    solution = dpll(bcp(cnf, variable), set_of_clauses + [variable])
    if not solution:
        solution = dpll(bcp(cnf, -variable), set_of_clauses + [-variable])


if __name__ == "__main__":
    num_minterms, num_vars, cnf = generate_cnf()
    set_of_clauses = create_clause_set(num_minterms,num_vars)

    # print(cnf)
    # print(set_of_clauses)

    # perform calculation
    if dpll(cnf, set_of_clauses):
        print("SAT")
    else:
        print("UNSAT")
