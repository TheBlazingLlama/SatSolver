import string
from collections import defaultdict

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
def generate_cube_list():
    num_vars = 0
    num_minterms = 0
    line = get_new_line_parsed()
    while is_comment(line):
        line = get_new_line_parsed()

    if is_preamble(line):
        cube_list = []
        num_vars = int(line[2])
        num_minterms = int(line[3])
        for i in range(num_minterms):
            eqn_line = get_new_line_parsed()
            cube = generate_cube(eqn_line, num_vars)
            cube_list.append(cube)

    return num_minterms, num_vars, cube_list

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

def dpll(cube_list):
    pass


if __name__ == "__main__":
    num_minterms, num_vars, cube_list = generate_cube_list()
    set_of_clauses = create_clause_set(num_minterms,num_vars)
    
    print(cube_list)
    print(set_of_clauses)