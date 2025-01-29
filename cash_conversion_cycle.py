from dataclasses import dataclass
from spreadsheet import SpreadSheet, ValueCell, FormulaCell
import pandas as pd

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
        self._spreadsheet = SpreadSheet(0, 4)

        # Year headers
        row = ["Year"] + [str(year) for year in range(1993, 1996)]
        self._spreadsheet.append_row(row)

        # Column Sub Headers
        row = ["Type"] + ["Actual" for _ in range(3)]
        self._spreadsheet.append_row(row)

        # Net Sales, Cogs, Discount, Operating Expense, Interest Expense
        for item in ['net_sales', 'cogs', 'discount', 'operating_expense', 'interest_expense']:
            row_name = item.replace("_", " ").title()
            row = [row_name] + income_statement[item]
            self._spreadsheet.append_row(row)
        
        # Pretax profits
        row = ['Pretax Profits'] + [f"{x}2 - {x}3 + {x}4 - {x}5 - {x}6" for x in "BCD"]
        self._spreadsheet.append_row(row, formula=True, skip_first=True)

        # Taxes
        row = ['Taxes'] + income_statement['taxes']
        self._spreadsheet.append_row(row)

        # Net income
        row = ['Net Income'] + [f"{x}7 - {x}8" for x in "BCD"]
        self._spreadsheet.append_row(row, formula=True, skip_first=True)

    def to_string(self, width: int = 5) -> str:
        return self._spreadsheet.to_string(width)

    def to_df(self):
        return self._spreadsheet.to_df()
    

if __name__ == "__main__":

    def process_data(df: pd.DataFrame) -> pd.DataFrame:
        # Rename columns
        df['value'] = df['value'].str.lower()
        df['value'] = df['value'].str.replace(" ", "_")
        df['value'] = df['value'].str.replace("(", "")
        df['value'] = df['value'].str.replace(")", "")
        df['value'] = df['value'].str.replace("&", "")
        df['value'] = df['value'].str.replace(",", "")
        df['value'] = df['value'].str.replace("/", "")

        # Transpose
        df = df.set_index('value').T

        return df
    
    data = pd.read_csv("clarkson.csv")

    data = process_data(data)

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

    print(ccc.to_df())