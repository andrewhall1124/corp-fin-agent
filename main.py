import string 
from typing import Optional

class FormulaCell:

    def __init__(self, formula: str) -> None:
        self._formula = formula
        self._value = None

    def evaluate(self) -> None:
        pass

    def get_value(self) -> None:
        return self._value

    def set_formula(self, formula: str) -> None:
        self._formula = formula

    def get_formulat(self) -> None:
        return self._formula

class ValueCell:

    def __init__(self, value: Optional[float] = 0):
        self._value = value

    def set_value(self, value: float) -> None:
        self._value = value

    def get_value(self) -> None:
        return self._value

class SpreadSheet:

    def __init__(self, num_rows: int, num_cols: int) -> None:
        self._cells = {
            char: [ValueCell() for _ in range(num_rows)] for char in string.ascii_uppercase[0: num_cols + 1]
        }

    def get_cell(self, loc: str) -> ValueCell | FormulaCell:
        col, row = loc[0], loc[1:]
        return self._cells[col][row]

    def set_cell(self, loc: str, cell: ValueCell | FormulaCell) -> None:
        col, row = loc[0], loc[1:]
        row = int(row) - 1

        self._cells[col][row] = cell

    def _evaluate(self) -> None:
        graph = self._get_dependencies()
        pass

    def _get_dependencies(self) -> None:
        pass

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

                result += f"{value:^5}"  # Center-align cell values with 5 spaces

            result += "\n"
        
        return result
            
if __name__ == "__main__":
    sheet = SpreadSheet(5, 5)
    print(sheet.to_string())

    sheet.set_cell(
        loc="A1",
        cell=ValueCell(5)
    )

    print(sheet.to_string())

    sheet.set_cell(
        loc="B1",
        cell=FormulaCell("A1 + 1")
    )

    print(sheet.to_string())

