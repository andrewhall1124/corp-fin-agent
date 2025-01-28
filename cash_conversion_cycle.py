from dataclasses import dataclass
from spreadsheet import SpreadSheet, ValueCell, FormulaCell
import pandas as pd
import polars as pl

@dataclass
class IncomeStatement:
    net_sales: float
    cogs: float
    discount: float
    operating_expense: float
    interest_expense: float
    taxes: float


class CashConversionCycle:

    def __init__(self, income_statement: dict[str, list[float]]) -> None:
        self._spreadsheet = SpreadSheet(10, 4)

        # Column Headers
        self._spreadsheet.set_cell("A0", ValueCell("Year"))
        self._spreadsheet.set_cell("B0", ValueCell("1993"))
        self._spreadsheet.set_cell("C0", ValueCell("1994"))
        self._spreadsheet.set_cell("D0", ValueCell("1995"))

        # Column Sub Headers
        self._spreadsheet.set_cell("A1", ValueCell("Type"))
        for x in "BCD":
            self._spreadsheet.set_cell(f"{x}1", ValueCell("Acutal"))

        # Net Sales, Cogs, Discount, Operating Expense, Interest Expense
        for i, key in zip(range(2, 7), list(income_statement.keys())[0:6]):

            self._spreadsheet.set_cell(f"A{i}", ValueCell(key.replace("_", " ").title()))

            for x, value in zip("BCD", income_statement[key]):

                self._spreadsheet.set_cell(f"{x}{i}", ValueCell(value))
        
        # Pretax profits
        self._spreadsheet.set_cell("A7", ValueCell("Pretax Profits"))
        for x in "BCD":
            self._spreadsheet.set_cell(f"{x}7", FormulaCell(f"{x}2 - {x}3 + {x}4 - {x}5 - {x}6"))

        # Taxes
        self._spreadsheet.set_cell("A8", ValueCell("Taxes"))
        for x, value in zip("BCD", income_statement['taxes']):
            self._spreadsheet.set_cell(f"{x}8", ValueCell(value))

        # Pretax profits
        self._spreadsheet.set_cell("A9", ValueCell("Net Income"))
        for x in "BCD":
            self._spreadsheet.set_cell(f"{x}9", FormulaCell(f"{x}7 - {x}8"))

    def to_string(self, width: int = 5) -> str:
        return self._spreadsheet.to_string(width)
    

if __name__ == "__main__":

    data = pd.read_csv("raw.csv")

    # Rename columns
    data['value'] = data['value'].str.lower()
    data['value'] = data['value'].str.replace(" ", "_")
    data['value'] = data['value'].str.replace("(", "")
    data['value'] = data['value'].str.replace(")", "")
    data['value'] = data['value'].str.replace("&", "")
    data['value'] = data['value'].str.replace(",", "")
    data['value'] = data['value'].str.replace("/", "")

    data = data.set_index('value').T

    income_statement = {
        'net_sales': data['net_sales'].to_list(),
        'cogs': data['cogs'].to_list(),
        'discount': data['discount'].to_list(),
        'operating_expense': data['operating_expense'].to_list(),
        'interest_expense': data['interest_expense'].to_list(),
        'taxes': data['taxes'].to_list()
    }

    ccc = CashConversionCycle(
        income_statement=income_statement
    )

    print(ccc.to_string(width=20))