class NQueens:
    def __init__(self, n):
        self.n = n
        self.result = [-1] * n
        self.solutions_backtracking = []
        self.solutions_branch_bound = []

    def is_safe(self, row, col):
        for prev_row in range(row):
            if (self.result[prev_row] == col or
                    self.result[prev_row] - prev_row == col - row or
                    self.result[prev_row] + prev_row == col + row):
                return False
        return True

    def backtracking_solve(self, row):
        if row == self.n:
            self.solutions_backtracking.append(self.result[:])
            return

        for col in range(self.n):
            if self.is_safe(row, col):
                self.result[row] = col
                self.backtracking_solve(row + 1)

    def branch_and_bound_solve(self):
        def backtrack(row):
            if row == self.n:
                self.solutions_branch_bound.append(self.result[:])
                return

            for col in range(self.n):
                if self.is_safe(row, col):
                    self.result[row] = col
                    backtrack(row + 1)
                    self.result[row] = -1  # Backtrack

        backtrack(0)

    def print_solutions(self, method):
        solutions = self.solutions_backtracking if method == "backtracking" else self.solutions_branch_bound
        for solution in solutions:
            for row in solution:
                print(" ".join("Q" if col == row else "-" for col in range(self.n)))
            print()

# Example usage:
n_queens = NQueens(4)
print("Solutions using Backtracking:")
n_queens.backtracking_solve(0)
n_queens.print_solutions("backtracking")

print("\nSolutions using Branch and Bound:")
n_queens.branch_and_bound_solve()
n_queens.print_solutions("branch_and_bound")
