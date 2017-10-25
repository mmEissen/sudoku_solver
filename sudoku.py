import itertools
import re

from ortools.constraint_solver import pywrapcp

BLOCK_SIZE = 3
PUZZLE_SIZE = BLOCK_SIZE ** 2

# Captures the sudoku in match group 1
RE_SUDOKU = re.compile(
    r'.*\n((?:\d{' + str(PUZZLE_SIZE) + '}\n){' + str(PUZZLE_SIZE) + '})'
)


def create_solver_vars(sudoku, solver):
    """Creates and returns IntVars for a given sudoku.
    """
    solver_vars = [
        solver.IntVar(number, number, str(i)) if number
        else solver.IntVar(1, PUZZLE_SIZE, str(i))
        for i, number in enumerate(sudoku)
    ]
    return solver_vars

def create_constraints(solver_vars, solver):
    """Creates constraints on the `solver_vars` and add the constraints to the
    solver.
    """
    lines = [
        solver_vars[i:i + PUZZLE_SIZE]
        for i in range(0, PUZZLE_SIZE ** 2, PUZZLE_SIZE)
    ]
    rows = zip(*lines)

    block_coords = itertools.product(range(0, PUZZLE_SIZE, BLOCK_SIZE), repeat=2)
    blocks = [
        [
            lines[y][x]
            for x, y in itertools.product(
                range(block_x, block_x + BLOCK_SIZE),
                range(block_y, block_y + BLOCK_SIZE),
            )
        ]
        for block_x, block_y in block_coords
    ]

    for section in itertools.chain(lines, rows, blocks):
        solver.Add(solver.AllDifferent(section))

def find_solution(solver, solver_vars):
    """Find a valid solution.
    """
    decision_builder = solver.Phase(
        solver_vars,
        solver.CHOOSE_FIRST_UNBOUND,
        solver.ASSIGN_MIN_VALUE,
    )

    solver.NewSearch(decision_builder)

    if solver.NextSolution():
        return [var.Value() for var in solver_vars]
    return []

def solve(sudoku):
    """Solve a sudoku.
    """

    # Initialize solver
    solver = pywrapcp.Solver('Sudoku Solver')

    # Define variables
    solver_vars = create_solver_vars(sudoku, solver)

    # Define constraints
    create_constraints(solver_vars, solver)

    # Solve
    solution = find_solution(solver, solver_vars)

    return solution or sudoku

def print_sudoku(sudoku):
    """Print a sudoku as a 9x9 block of digits.
    """
    for i in range(0, PUZZLE_SIZE ** 2, PUZZLE_SIZE):
        print(''.join(str(n) for n in sudoku[i:i + PUZZLE_SIZE]))
    print()

def load_sudokus(file_name):
    """Load sudokus from a file. The file is expected to have one sudoku in every line
    """
    with open(file_name) as sudoku_file:
        sudokus = [[int(c) for c in line.strip()] for line in sudoku_file]
    return sudokus

def main():
    sudokus = load_sudokus('sudoku_data.txt')
    for sudoku in sudokus:
        print_sudoku(solve(sudoku))

if __name__ == '__main__':
    main()
