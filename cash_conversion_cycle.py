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

    def __init__(self, income_statement: dict[str, list[float]], balance_sheet: dict[str, list[float]]) -> None:
        self._spreadsheet = SpreadSheet(0, 9)
        self._header()
        self._key_assumptions()
        self._cash_conversion_cycle()
        self._income_statement(income_statement)
        self._balance_sheet(balance_sheet)

    def _header(self):
        # Year headers
        row = ["Year"] + [str(year) for year in range(1993, 2000)] + ['Percent of Sales']
        self._spreadsheet.append_row(row)

        # Column Sub Headers
        row = ["Type"] + ["Actual" for _ in range(3)] + ["Forecast" for _ in range(4)]
        self._spreadsheet.append_row(row)
    
    def _key_assumptions(self):
        # Sales Growth
        historical = [None] + [FormulaCell(f"( {y}6 - {x}6 ) / {x}6") for x, y in ["BC", "CD"]]
        forecast = [ValueCell(.25) for _ in range(4)]
        row = ['Sales Growth'] + historical + forecast
        self._spreadsheet.append_row(row)

        # Interest Rate
        row = ['Interest Rate'] + [None for _ in range(3)] + [.11 for _ in range(4)]
        self._spreadsheet.append_row(row)

        # Tax Rate
        historical = [FormulaCell(f"{x}12 / {x}11") for x in "BCD"]
        row = ['Tax Rate'] + historical
        self._spreadsheet.append_row(row)

    def _cash_conversion_cycle(self):
        # Payables Period
        row = ['Payables Period'] + [FormulaCell(f"( {x}21 + {x}22 ) / ( {x}7 / 365 )") for x in "BCD"]
        self._spreadsheet.append_row(row)

    def _income_statement(self, income_statement: dict[str, list[float]]):
        # Net Sales
        row = ['Net Sales'] + income_statement['net_sales']
        self._spreadsheet.append_row(row)

        # Cogs
        row = ['COGS'] + income_statement['cogs']
        self._spreadsheet.append_row(row)

        # Discount
        row = ['Discount'] + income_statement['discount']
        self._spreadsheet.append_row(row)

        # Operating Expense
        row = ['Operating Expense'] + income_statement['operating_expense']
        self._spreadsheet.append_row(row)

        # Interest Expense
        row = ['Interest Expense'] + income_statement['interest_expense']
        self._spreadsheet.append_row(row)
        
        # Pretax profits
        row = ['Pretax Profits'] + [FormulaCell(f"{x}6 - {x}7 + {x}8 - {x}9 - {x}10") for x in "BCD"]
        self._spreadsheet.append_row(row)

        # Taxes
        row = ['Taxes'] + income_statement['taxes']
        self._spreadsheet.append_row(row)

        # Net income
        row = ['Net Income'] + [FormulaCell(f"{x}11 - {x}12") for x in "BCD"]
        self._spreadsheet.append_row(row)

    def _balance_sheet(self, balance_sheet: dict[str, list[float]]):
        # Cash
        row = ['Cash'] + balance_sheet['cash']
        self._spreadsheet.append_row(row)

        # A/R
        row = ['A/R'] + balance_sheet['ar']
        self._spreadsheet.append_row(row)

        # Inventory
        row = ['Inventory'] + balance_sheet['inventory']
        self._spreadsheet.append_row(row)

        # PP&E
        row = ['PP&E'] + balance_sheet['ppe']
        self._spreadsheet.append_row(row)

        # Total Assets
        row = ['Total Assets'] + [FormulaCell(f"{x}14 + {x}15 + {x}16 + {x}17") for x in "BCD"]
        self._spreadsheet.append_row(row)

        # Notes Payable (PLUG)
        row = ['Notes Payable (PLUG)'] + balance_sheet['notes_payable_bank_plug']
        self._spreadsheet.append_row(row)

        # Notes Payable Holtz
        row = ['Notes Payable Holtz'] + balance_sheet['note_payable_to_holtz']
        self._spreadsheet.append_row(row)

        # Notes Payable Trade
        row = ['Notes Payable Trade'] + balance_sheet['notes_payable_trade']
        self._spreadsheet.append_row(row)

        # A/P
        row = ['A/P'] + balance_sheet['ap']
        self._spreadsheet.append_row(row)

        # Accrued Expenses
        row = ['Accrued Expenses'] + balance_sheet['accrued_expenses']
        self._spreadsheet.append_row(row)

        # Term Loan Current Portion
        row = ['Term Loan Current Portion'] + balance_sheet['term_loan_current_portion']
        self._spreadsheet.append_row(row)

        # Term Loan
        row = ['Term Loan'] + balance_sheet['term_loan']
        self._spreadsheet.append_row(row)

        # Net Worth
        row = ['Net Worth'] + balance_sheet['net_worth']
        self._spreadsheet.append_row(row)

        # Total Liabilities
        row = ['Total Liabilities'] + [FormulaCell(f"{x}19 + {x}20 + {x}21 + {x}22 + {x}23 + {x}24 + {x}25 + {x}26") for x in "BCD"]
        self._spreadsheet.append_row(row)

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

    balance_sheet = {
        'cash': data['cash'].to_list(),
        'ar': data['ar'].to_list(),
        'inventory': data['inventory'].to_list(),
        'ppe': data['ppe'].to_list(),
        'notes_payable_bank_plug': data['notes_payable_bank_plug'].to_list(),
        'note_payable_to_holtz': data['note_payable_to_holtz'].to_list(),
        'notes_payable_trade': data['notes_payable_trade'].to_list(),
        'ap': data['ap'].to_list(),
        'accrued_expenses': data['accrued_expenses'].to_list(),
        'term_loan_current_portion': data['term_loan_current_portion'].to_list(),
        'term_loan': data['term_loan'].to_list(),
        'net_worth': data['net_worth'].to_list()
    }

    ccc = CashConversionCycle(
        income_statement=income_statement,
        balance_sheet=balance_sheet
    )

    print(ccc.to_df())