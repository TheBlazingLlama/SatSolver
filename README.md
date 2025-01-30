'''
EDA for VSLI Circuits I - ECE-C671
Project 2 - SAT Solver
Varun Iyengar, Cassius Garcia, Harrison Muller

'''

'''
Description
For this project, students were tasked with building a SAT solver. Our group built a SAT solver using DPLL, which we optimized using speedy heuristics and parallelism to reduce the time spent on certain computations. Information on how to execute the code and run certain benchmarks is included below.
'''

'''
Execution
To run the file, run the code below

	$ python satSolver_parallel.py 

The code will provide the following prompt. Please input the benchmark file you would like to run

	Input the file you would like to read from: __filename__

If you would like to print out illuminating information, such as backtracks and the values computed, please input the filename followed by -l

	Input the file you would like to read from: __filename__ -l

'''
Output
The code should output whether the CNF is SAT or UNSAT, CPU time, # of backtracks, and the literal assignments.
'''
