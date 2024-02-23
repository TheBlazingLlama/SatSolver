import string

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

    return cube_list

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

if __name__ == "__main__":
    cube_list = generate_cube_list()
    print(cube_list)