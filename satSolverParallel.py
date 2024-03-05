import string
from collections import defaultdict
import multiprocessing
import time

l = False;
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
def generate_cnf_value_based():
    num_vars = 0
    num_minterms = 0
    file_name = input("Input the file you would like to read from: ")
    if(file_name[-2:] == "-l"):
        global l
        l = True
        file_name = file_name[:-3]
    lines = get_lines_cleaned(file_name)
    cnf = []
    for line in lines:
        if is_comment(line):
            continue
        if is_preamble(line):
            num_vars = int(line[2])
            num_minterms = int(line[3])
        else:
            line = list(map(int, line))
            cnf.append(line)

    return num_minterms, num_vars, cnf


# Returns varible to split on. When calling backtrack method call as such - backtrack(cnf, jersolow_wang(cnf))
# If no solution from that then try - backtrack(cnf, -jersolow_wang(cnf)) to negate 
# Approx 50% speed increase from standard jersolow wang
def jersolow_wang_worker(chunk_cnf, result_queue):
    literal_weight = defaultdict(int)
    for clause in chunk_cnf:
        for literal in clause:
            literal_weight[abs(literal)] += 2 ** -len(clause)
    result_queue.put(literal_weight)

def jersolow_wang_2_sided_method(cnf):
    num_processes = multiprocessing.cpu_count()
    chunk_size = len(cnf) // num_processes
    manager = multiprocessing.Manager()
    result_queue = manager.Queue()
    processes = []

    for i in range(num_processes):
        start_idx = i * chunk_size
        end_idx = start_idx + chunk_size if i < num_processes - 1 else len(cnf)
        chunk_cnf = cnf[start_idx:end_idx]
        p = multiprocessing.Process(target=jersolow_wang_worker, args=(chunk_cnf, result_queue))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    combined_literal_weight = defaultdict(int)
    while not result_queue.empty():
        literal_weight = result_queue.get()
        for literal, weight in literal_weight.items():
            combined_literal_weight[literal] += weight

    return max(combined_literal_weight, key=combined_literal_weight.get)

# Somewhat standard among most DPLL implementations, input is cnf and the splitting variable, output is new cnf
def bcp_worker(chunk_cnf, unit, flag, result_queue):
    new_cnf = []
    if flag == 1:
        unit_literal = unit
        neg_unit_literal = -unit
    elif flag == 2:
        unit_literal = -unit
        neg_unit_literal = unit
        
    for clause in chunk_cnf:
        if unit_literal in clause:
            continue
        if neg_unit_literal in clause:
            new_clause = [literal for literal in clause if literal != neg_unit_literal]
            if not new_clause:
                result_queue.put(-1)
                return
            new_cnf.append(new_clause)
        else:
            new_cnf.append(clause)
    result_queue.put(new_cnf)
# use 1 for flag if positive and 2 if complemented
def bcp_parallel(cnf, unit, flag):
    processes = []
    num_processes = multiprocessing.cpu_count()
    chunk_size = len(cnf) // num_processes
    manager = multiprocessing.Manager()
    result_queue = manager.Queue()
    
    for i in range(num_processes):
        start_idx = i * chunk_size
        end_idx = start_idx + chunk_size if i < num_processes - 1 else len(cnf)
        chunk_cnf = cnf[start_idx:end_idx]
        p = multiprocessing.Process(target=bcp_worker, args=(chunk_cnf, unit, flag, result_queue))
        processes.append(p)
        p.start()
    
    for p in processes:
        p.join()
    
    new_cnf = []
    while not result_queue.empty():
        result = result_queue.get()
        if result == -1:
            return -1
        else:
            new_cnf.extend(result)
    
    return new_cnf

def if_one_literal(clause):
    count_one = 0
    #print(clause)
    for literal in clause:
        if literal != 0:
            count_one += 1
    if count_one == 1:
        return 1
    return 0
    
# Perform unit propagation. Standard across most DPLL implementations seen.
def unit_propagation_parallel(cnf):
    row = 0
    assignment = []
    unit_clauses = []

    for clause in cnf:
        if len(clause) == 1:
            unit_clauses.append(clause)
    
    for clause in cnf:
      if if_one_literal(clause)==1:
        if l:
            print("one literal clause is " + str(clause))
        unit_clauses.append(clause)
        
    while unit_clauses:
        literal = unit_clauses[0]
        index = literal[0]
        cnf = bcp_parallel(cnf, index, 1)
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

# Check if all clauses evaluate to 1 (if set of clauses is empty)
def clauses_all_one(set_of_clauses):

    if isinstance(set_of_clauses,int):
        return 0

    if len(set_of_clauses) == 0:
        return 1
    else:
        return 0
    
def all_dc(clause):
    if not clause:
        return 1
    return 0

# Check if any clause evaluates to 0
def clauses_unsat(set_of_clauses):
    if set_of_clauses == -1:
        return 1
    return 0

def print_nested_clauses(set_of_clauses):
    for item in set_of_clauses:
        if isinstance(item, list):
            print_nested_clauses(item)
        else:
            print(item,end=' ')

def print_info(cnf, unit_assignment, set_of_clauses):
    print(f'CNF: {cnf}')
    print(f'Unit Assignment: {unit_assignment}')
    print(f'Set of Clauses: ')
    print_nested_clauses(set_of_clauses)
    print()

def dpll_parallel(cnf, set_of_clauses):
    
    # Call Unit Proagation to perform BCP.
    cnf, unit_assignment= unit_propagation_parallel(cnf)
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
    
    solution = dpll_parallel(bcp_parallel(cnf, variable, 1), set_of_clauses + [variable])
    if not solution:
        if l:
            print("backtrack")
        solution = dpll_parallel(bcp_parallel(cnf, variable, 2), set_of_clauses + [-variable])
    return solution


if __name__ == "__main__":
    if __name__ == "__main__":
    start_time = time.process_time()
    # num_minterms, num_vars, cnf = generate_cnf()
    num_minterms, num_vars, cnf = generate_cnf_value_based()
    set_of_clauses = []
    print(cnf)

    # perform calculation
    result = dpll_parallel(cnf, set_of_clauses)
    if result:
        print("SATISFIABLE")
        print(result)
    else:
        print("UNSATISFIABLE")

    end_time = time.process_time()

    elapsed_time = end_time - start_time
    print("Elapsed time:", elapsed_time, "seconds")

