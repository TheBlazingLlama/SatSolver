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

        while "0" in split_line: 
            split_line.remove("0")

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
    print(lines)
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

# Generate the cube list
def generate_cnf_value_based():
    num_vars = 0
    num_minterms = 0
    file_name = input("Input the file you would like to read from: ")
    lines = get_lines_cleaned(file_name)
    print(lines)
    cnf = []
    for line in lines:
        if is_comment(line):
            continue
        if is_preamble(line):
            num_vars = int(line[2])
            num_minterms = int(line[3])
        else:
            #cube = generate_cube(line, num_vars)
            line = list(map(int, line))
            cnf.append(line)

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
# Returns varible to split on. When calling backtrack method call as such - backtrack(cnf, jersolow_wang(cnf))
# If no solution from that then try - backtrack(cnf, -jersolow_wang(cnf)) to negate 
# Approx 50% speed increase from standard jersolow wang
def jersolow_wang_2_sided_method(cnf):
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

# Somewhat standard among most DPLL implementations, input is cnf and the splitting variable, output is new cnf
def bcp(cnf, unit):
    modified = []
    #if flag == 1:
    #  polarity = 1
    #  cnf_p = deepcopy(cnf)
    #  for clause in cnf_p:
    #    clause[unit] = 1
    # Add functionality here
    for clause in cnf:
        if clause[unit] == 1:
            continue
        if clause[unit] == 2:
            clause[unit] = 0
            new_clause = clause
            if not new_clause:
                return -1
            modified.append(new_clause)
        else:
            #modified_clause = []
            #for literal in clause:
            #    if literal == unit:
            #        modified_clause.append(1 if polarity == 'positive' else 2)
            #    else:
            #        modified_clause.append(0)
            #modified.append(modified_clause)
            modified.append(clause)
    #print(modified)
    return modified

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
  index = 0
  for literal in clause:
      if literal == 0:
          index += 1 
  return index

    
# Perform unit propagation. Standard across most DPLL implementations seen.
def unit_propagation(cnf):
    row = 0
    assignment = []
    unit_clauses = []
    
    for clause in cnf:
      if if_one_literal(clause)==1:
        unit_clauses.append(clause)
        row += 1
        
    while unit_clauses:
        #print(f'unit_clause: {unit_clauses}')
        unit = unit_clauses[0]
        #print(f'unit: {unit}')
        index = unit_index(unit)
        #print(f'index: {index}')
        cnf = bcp(cnf, index)
        assignment += [unit]
        #print(f'cnf: {cnf}')
        #print(f'row: {row}')
        if clauses_unsat(cnf): #cnf == -1:
            return -1, []
        if clauses_all_one(cnf):#not cnf:
            return cnf, assignment
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
        if all_dc(clause):
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
    set_of_clauses[row] = unit_assignment[0]
    print(f'soc: {set_of_clauses}')
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
    set_of_clauses[variable] = 1
    solution = dpll(bcp(cnf, variable), set_of_clauses)
    if not solution:
        set_of_clauses[variable] = 2
        solution = dpll(bcp(cnf, variable), set_of_clauses)
    return solution


if __name__ == "__main__":
    # num_minterms, num_vars, cnf = generate_cnf()
    num_minterms, num_vars, cnf = generate_cnf_value_based()
    set_of_clauses = create_clause_set(num_minterms,num_vars)

    print(cnf)
    # print(set_of_clauses)

    # perform calculation
    if dpll(cnf, set_of_clauses):
        print("SAT")
    else:
        print("UNSAT")
