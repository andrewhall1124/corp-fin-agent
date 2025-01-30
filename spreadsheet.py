import string
from typing import Optional
from collections import defaultdict
import pandas as pd


class FormulaCell:

    def __init__(self, formula: str) -> None:
        self._formula = formula
        self._value = 0.0

    @property
    def value(self) -> float:
        """Gets the value."""
        return self._value

    @value.setter
    def value(self, value: float) -> None:
        """Sets the value."""
        self._value = value

    @property
    def formula(self) -> str:
        """Gets the formula."""
        return self._formula

    @formula.setter
    def formula(self, formula: float) -> None:
        """Sets the formula."""
        self._formula = formula

    def get_dependencies(self) -> set[str]:
        """Get's the dependencies of the formula cell."""
        tokens = self._formula.split()
        deps = set()
        for token in tokens:
            if token[0] in string.ascii_uppercase and token[1:].isdigit():
                deps.add(token)
        return deps


class ValueCell:
    def __init__(self, value: Optional[float] = None):
        self._value = value

    @property
    def value(self) -> float:
        """Gets the value."""
        return self._value

    @value.setter
    def value(self, value: float) -> None:
        """Sets the value."""
        self._value = value


class SpreadSheet:

    def __init__(self, num_rows: int = 0, num_cols: int = 0) -> None:
        self._row_keys = list(range(0, num_rows))
        self._col_keys = list(string.ascii_uppercase[0:num_cols])

        self._cells = [
            {char: ValueCell() for char in self._col_keys} for _ in self._row_keys
        ]

    def get_cell(self, cell_loc: str) -> ValueCell | FormulaCell:
        """Gets the cell at the cell location."""
        col, row = cell_loc[0], int(cell_loc[1:])
        return self._cells[row][col]

    def set_cell(self, loc: str, cell: ValueCell | FormulaCell) -> None:
        """Sets the cell at the specified location."""
        col, row = loc[0], int(loc[1:])
        self._cells[row][col] = cell

    def add_column(self, num: int = 1):
        for _ in range(num):
            last_col = self._col_keys[-1]
            new_col = chr(ord(last_col) + 1)

            for row in self._cells:
                row[new_col] = ValueCell()

            self._col_keys.append(new_col)

    def add_row(self, num: int = 1):
        for _ in range(num):
            self._cells.append({char: ValueCell() for char in self._col_keys})
            self._row_keys.append(len(self._row_keys))

    def append_row(self, cells: list[float]) -> None:

        num_empty_values = len(self._col_keys) - len(cells)

        for i, cell in enumerate(cells):
            if not isinstance(cell, ValueCell) and not isinstance(cell, FormulaCell):
                cells[i] = ValueCell(cell)

        cells = cells + [ValueCell() for _ in range(num_empty_values)]

        self._cells.append({char: cell for char, cell in zip(self._col_keys, cells)})

        new_row = len(self._row_keys)
        self._row_keys.append(new_row)

    def _evaluate(self) -> None:
        """Evaluates each formula cell in topological order."""

        # Get dependency graph
        graph = self._get_dependencies()

        # Initialize
        visited = set()
        temp_visited = set()
        order: list[str] = []

        # Recursive depth first search algorithm
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
        for col in self._col_keys:
            for row in self._row_keys:

                cell_loc = f"{col}{row}"

                if cell_loc not in visited:
                    dfs(cell_loc)

        # Evaluate cells in topological order
        for cell_loc in order:
            col, row = cell_loc[0], int(cell_loc[1:])
            cell = self._cells[row][col]

            if isinstance(cell, FormulaCell):
                self._evaluate_cell(cell_loc)

    def _get_dependencies(self) -> dict[str, set[str]]:
        """Build adjacency list representation of dependencies"""

        # Initialize
        graph = defaultdict(set)

        # Traverse each cell
        for col in self._col_keys:
            for row in self._row_keys:

                cell_loc = f"{col}{row}"
                cell = self.get_cell(f"{col}{row}")

                if isinstance(cell, FormulaCell):

                    # Add edges from this cell to its dependencies
                    deps = cell.get_dependencies()
                    for dep in deps:
                        graph[cell_loc].add(dep)
        return graph

    def _evaluate_cell(self, cell_loc: str) -> None:
        """Compute the result of a formula cell."""

        # Initialize
        cell = self.get_cell(cell_loc)
        eval_formula = cell.formula

        # Replace each dependency with its value
        for dep_loc in cell.get_dependencies():

            dep_cell = self.get_cell(dep_loc)
            dep_value = dep_cell.value

            eval_formula = eval_formula.replace(dep_loc, str(dep_value))

        # Evaluate the formula using Python's eval
        result = eval(eval_formula)
        cell.value = result

        # Set cell value
        self.set_cell(cell_loc, cell)

    def to_string(self, width: int = 5) -> str:
        """Evaluates all formula cells and returns a string representation of the spreadsheet."""
        self._evaluate()
        result = "   "

        # Add column headers
        for col in self._col_keys:

            result += f"{col:^{width}}"  # Center-align column headers with 5 spaces

        result += "\n"

        # Add rows with row numbers and cell values
        for row in self._row_keys:

            result += f"{row:2d} "  # Add row number with 2 digits of space

            # Add cell values for each column
            for col in self._col_keys:

                cell = self.get_cell(f"{col}{row}")
                value = cell.value

                if value is None:
                    value = ""

                result += (
                    f"{value:^{width}.1f}"
                    if isinstance(value, float)
                    else f"{value:^{width}}"
                )

            result += "\n"

        return result

    def to_df(self):
        self._evaluate()
        data = []
        for row in self._cells:
            new_row = {key: cell.value for key, cell in row.items()}
            data.append(new_row)

        return pd.DataFrame(data).fillna("")


if __name__ == "__main__":
    sheet = SpreadSheet()

    print(sheet.to_string())

    sheet.add_column()

    print(sheet.to_string())

    sheet.add_row()

    print(sheet.to_string())
    # # Create Spreadsheet instance
    # sheet = SpreadSheet(2, 2)
    # print(sheet.to_string())

    # # Set cell A1 to 5.0
    # sheet.set_cell(loc="A0", cell=ValueCell(5.0))
    # print(sheet.to_string())

    # # Set cell A2 to A1 + 1
    # sheet.set_cell(loc="A1", cell=FormulaCell("A0 + 1"))
    # print(sheet.to_string())

    # # Set cell B2 to A2 * 2
    # sheet.set_cell(loc="B1", cell=FormulaCell("A1 * 2"))
    # print(sheet.to_string())

    # # Change cell A1 to 6
    # sheet.set_cell(loc="A0", cell=ValueCell(6.0))
    # print(sheet.to_string())
