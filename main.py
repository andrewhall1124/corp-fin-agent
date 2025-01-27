import string
from typing import Optional
from collections import defaultdict


class FormulaCell:

    def __init__(self, formula: str) -> None:
        self._formula = formula
        self._value = None

    def get_value(self) -> float:
        return self._value

    def set_value(self, value: float) -> None:
        self._value = value

    def set_formula(self, formula: str) -> None:
        self._formula = formula

    def get_formula(self) -> str:
        return self._formula

    def get_dependencies(self) -> set[str]:
        # Return cell references in the formula
        tokens = self._formula.split()
        deps = set()
        for token in tokens:
            if token[0] in string.ascii_uppercase and token[1:].isdigit():
                deps.add(token)
        return deps


class ValueCell:

    def __init__(self, value: Optional[float] = 0.0):
        self._value = value

    def set_value(self, value: float) -> None:
        self._value = value

    def get_value(self) -> float:
        return self._value


class SpreadSheet:

    def __init__(self, num_rows: int, num_cols: int) -> None:
        self._cells = {
            char: [ValueCell() for _ in range(num_rows)]
            for char in string.ascii_uppercase[0:num_cols]
        }

    def get_cell(self, loc: str) -> ValueCell | FormulaCell:
        col, row = loc[0], loc[1:]
        row = int(row) - 1
        return self._cells[col][row]

    def set_cell(self, loc: str, cell: ValueCell | FormulaCell) -> None:
        col, row = loc[0], loc[1:]
        row = int(row) - 1

        self._cells[col][row] = cell

    def _evaluate(self) -> None:
        # Get dependency graph
        graph = self._get_dependencies()

        # Find evaluation order using topological sort
        visited = set()
        temp_visited = set()
        order: list[str] = []

        def dfs(cell_loc: str) -> None:
            if cell_loc in temp_visited:
                raise ValueError("Circular dependency detected")

            if cell_loc in visited:
                return

            temp_visited.add(cell_loc)

            for dep in graph[cell_loc]:
                dfs(dep)

            temp_visited.remove(cell_loc)
            visited.add(cell_loc)
            order.append(cell_loc)

        # Run DFS for each cell
        for col in self._cells:
            for row in range(len(self._cells[col])):

                cell_loc = f"{col}{row + 1}"

                if cell_loc not in visited:
                    dfs(cell_loc)

        # Evaluate cells in topological order
        for cell_loc in order:
            col, row = cell_loc[0], int(cell_loc[1:]) - 1
            cell = self._cells[col][row]

            if isinstance(cell, FormulaCell):
                self._evaluate_cell(cell_loc)

    def _get_dependencies(self) -> dict[str, set[str]]:
        # Build adjacency list representation of dependencies
        graph = defaultdict(set)

        for col in self._cells:
            for row in range(len(self._cells[col])):

                cell_loc = f"{col}{row + 1}"
                cell = self._cells[col][row]

                if isinstance(cell, FormulaCell):

                    # Add edges from this cell to its dependencies
                    deps = cell.get_dependencies()
                    for dep in deps:
                        graph[cell_loc].add(dep)
        return graph

    def _evaluate_cell(self, loc: str) -> None:
        cell = self.get_cell(loc)

        formula = cell.get_formula()

        # Get all cell references
        deps = cell.get_dependencies()

        # Replace each cell reference with its value
        eval_formula = formula

        for dep in deps:

            dep_cell = self.get_cell(dep)
            dep_value = dep_cell.get_value()

            if dep_value is None:
                cell.set_value(0.0)
                return

            # Replace the cell reference with its value
            eval_formula = eval_formula.replace(dep, str(dep_value))

        # Evaluate the formula using Python's eval
        result = eval(eval_formula)
        cell.set_value(float(result))

        self.set_cell(loc, cell)

    def to_string(self):
        self._evaluate()
        result = "   "

        # Add column headers
        for col in sorted(self._cells.keys()):

            result += f"{col:^5}"  # Center-align column headers with 5 spaces

        result += "\n"

        # Add rows with row numbers and cell values
        for row_idx in range(len(next(iter(self._cells.values())))):

            result += f"{row_idx + 1:2d} "  # Add row number with 2 digits of space

            # Add cell values for each column
            for col in sorted(self._cells.keys()):

                cell = self._cells[col][row_idx]
                value = cell.get_value()

                if value is None:
                    value = ""
                result += f"{value:^5.1f}"  # Center-align cell values with 5 spaces

            result += "\n"

        return result


if __name__ == "__main__":
    # Create Spreadsheet instance
    sheet = SpreadSheet(2, 2)
    print(sheet.to_string())

    # Set cell A1 to 5.0
    sheet.set_cell(loc="A1", cell=ValueCell(5.0))
    print(sheet.to_string())

    # Set cell A2 to A1 + 1
    sheet.set_cell(loc="A2", cell=FormulaCell("A1 + 1"))
    print(sheet.to_string())

    # Set cell B2 to A2 * 2
    sheet.set_cell(loc="B2", cell=FormulaCell("A2 * 2"))
    print(sheet.to_string())

    # Change cell A1 to 6
    sheet.set_cell(loc="A1", cell=ValueCell(6.0))
    print(sheet.to_string())
