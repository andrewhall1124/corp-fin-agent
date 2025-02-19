from dataclasses import dataclass
import dao
import pandas as pd
import string

from spreadsheet import FormulaCell, SpreadSheet, Style, ValueCell
from statements import IncomeStatement, BalanceSheet

R = {
    'sales_growth': 3,
    'interest_rate': 4,
    'tax_rate': 5,
    'net_sales': 14,
    'ebt': 22,
    'taxes': 24
}


class CashConversionCycle:

    def __init__(
        self,
        income_statement: IncomeStatement,
        balance_sheet: BalanceSheet,
        sales_growth: float,
        interest_rate: float,
        num_forecast_cols: int,
    ) -> None:

        diff1 = set(income_statement.year) - set(balance_sheet.year)
        diff2 = set(balance_sheet.year) - set(income_statement.year)

        if len(diff1) > 0 or len(diff2) > 0:
            msg = "Income and Balance Statement years do not match."
            raise ValueError(msg)
        
        historical_years = income_statement.year
        num_historical_cols = len(income_statement.year)

        forecast_years = [max(historical_years) + i for i in range(1, num_forecast_cols + 1)]
        years = sorted(historical_years) + sorted(forecast_years)

        total_columns = 2 + num_historical_cols + num_forecast_cols
        self._columns = string.ascii_uppercase[0:total_columns]

        self._spreadsheet = SpreadSheet(0, total_columns)
        self._header(years)
        self._key_assumptions(sales_growth, interest_rate)
        # self._cash_conversion_cycle()
        # self._income_statement(income_statement)
        # self._balance_sheet(balance_sheet)

    def _header(self, years):
        # Year headers
        row = (
            ["Year"] + [str(year) for year in years] + ["Percent of Sales"]
        )
        self._spreadsheet.append_row(row)

        # Column Sub Headers
        row = ["Item"] + ["Actual" for _ in range(3)] + ["Forecast" for _ in range(4)]
        self._spreadsheet.append_row(row)

    def _key_assumptions(self, sales_growth: float, interest_rate: float):
        # Section Header
        row = ['Key Assumptions']
        self._spreadsheet.append_row(row)

        # Sales Growth
        historical = [None] + [
            FormulaCell(f"( {y}{R['net_sales']} - {x}{R['net_sales']} ) / {x}{R['net_sales']}", Style.Percent)
            for x, y in zip("BC", "CD")
        ]
        forecast = [ValueCell(sales_growth, Style.Percent) for _ in range(4)]
        row = ["Sales Growth"] + historical + forecast
        self._spreadsheet.append_row(row)

        # Interest Rate
        row = (
            ["Interest Rate"]
            + [None for _ in range(3)]
            + [ValueCell(interest_rate, Style.Percent) for _ in range(4)]
        )
        self._spreadsheet.append_row(row)

        # Tax Rate
        historical = [FormulaCell(f"{x}{R['taxes']} / {x}{R['ebt']}", Style.Percent) for x in "BCD"]
        forecast = [FormulaCell(f"{x}{R['tax_rate']}", Style.Percent) for x in "DEFG"]
        row = ["Tax Rate"] + historical + forecast
        self._spreadsheet.append_row(row)

    def _cash_conversion_cycle(self):
        # Payables Period
        historical = [FormulaCell(f"( {x}21 + {x}22 ) / ( {x}7 / 365 )") for x in "BCD"]
        forecast = [FormulaCell(f"{x}5") for x in "DEFG"]
        row = ["Payables Period"] + historical + forecast
        self._spreadsheet.append_row(row)

    def _income_statement(self, income_statement: IncomeStatement):
        # Net Sales
        historical = income_statement.net_sales
        forecast = [FormulaCell(f"{x}6 * ( 1 + {y}2 )") for x, y in zip("DEFG", "EFGH")]
        row = ["Net Sales"] + historical + forecast
        self._spreadsheet.append_row(row)

        # Cogs
        historical = income_statement.cost_of_goods_sold
        forecast = [FormulaCell(f"{x}6 * I7") for x in "EFGH"]
        percent_of_sales = [
            FormulaCell("sum([ B7 / B6 , C7 / C6 , D7 / D6 ]) / 3", Style.Percent)
        ]
        row = ["COGS"] + historical + forecast + percent_of_sales
        self._spreadsheet.append_row(row)

        # Discount (fix later)
        row = ["Discount"] + [0] * 3 + [0 for _ in range(4)]
        self._spreadsheet.append_row(row)

        # Operating Expense
        historical = income_statement.operating_expense
        forecast = [FormulaCell(f"{x}6 * I9") for x in "EFGH"]
        percent_of_sales = [
            FormulaCell("sum([ B9 / B6 , C9 / C6 , D9 / D6 ]) / 3", Style.Percent)
        ]
        row = ["Operating Expense"] + historical + forecast + percent_of_sales
        self._spreadsheet.append_row(row)

        # Interest Expense
        historical = income_statement.interest_expense
        forecast = [FormulaCell(f"{x}3 * {y}19") for x, y in zip("EFGH", "DEFG")]
        row = ["Interest Expense"] + historical + forecast
        self._spreadsheet.append_row(row)

        # Pretax profits
        row = ["Pretax Profits"] + [
            FormulaCell(f"{x}6 - {x}7 + {x}8 - {x}9 - {x}10") for x in "BCDEFGH"
        ]
        self._spreadsheet.append_row(row)

        # Taxes
        historical = income_statement.taxes
        forecast = [FormulaCell(f"{x}4 * {x}11") for x in "EFGH"]
        row = ["Taxes"] + historical + forecast
        self._spreadsheet.append_row(row)

        # Net income
        row = ["Net Income"] + [FormulaCell(f"{x}11 - {x}12") for x in "BCDEFGH"]
        self._spreadsheet.append_row(row)

    def _balance_sheet(self, balance_sheet: BalanceSheet):
        # Cash
        historical = balance_sheet.cash
        forecast = [FormulaCell(f"{x}6 * I14") for x in "EFGH"]
        percent_of_sales = [
            FormulaCell("sum([ B14 / B6 , C14 / C6 , D14 / D6 ]) / 3", Style.Percent)
        ]
        row = ["Cash"] + historical + forecast + percent_of_sales
        self._spreadsheet.append_row(row)

        # A/R
        historical = balance_sheet.accounts_recievable
        forecast = [FormulaCell(f"{x}6 * I15") for x in "EFGH"]
        percent_of_sales = [
            FormulaCell("sum([ B15 / B6 , C15 / C6 , D15 / D6 ]) / 3", Style.Percent)
        ]
        row = ["A/R"] + historical + forecast + percent_of_sales
        self._spreadsheet.append_row(row)

        # Inventory
        historical = balance_sheet.inventory
        forecast = [FormulaCell(f"{x}6 * I16") for x in "EFGH"]
        percent_of_sales = [
            FormulaCell("sum([ B16 / B6 , C16 / C6 , D16 / D6 ]) / 3", Style.Percent)
        ]
        row = ["Inventory"] + historical + forecast + percent_of_sales
        self._spreadsheet.append_row(row)

        # PP&E
        historical = balance_sheet.property_plant_and_equipment
        forecast = [FormulaCell(f"{x}6 * I17") for x in "EFGH"]
        percent_of_sales = [
            FormulaCell("sum([ B17 / B6 , C17 / C6 , D17 / D6 ]) / 3", Style.Percent)
        ]
        row = ["PP&E"] + historical + forecast + percent_of_sales
        self._spreadsheet.append_row(row)

        # Total Assets
        row = ["Total Assets"] + [
            FormulaCell(f"sum([ {x}14 , {x}15 , {x}16 , {x}17 ])") for x in "BCDEFGH"
        ]
        self._spreadsheet.append_row(row)

        # Notes Payable (PLUG)
        historical = balance_sheet.short_term_debt
        forecast = [
            FormulaCell(f"{x}18 - sum([ {x}22 , {x}23 , {x}24 , {x}25 , {x}26 ])")
            for x in "EFGH"
        ]
        row = ["Short Term Debt (PLUG)"] + historical + forecast
        self._spreadsheet.append_row(row)

        # A/P
        forecast = [FormulaCell(f"{x}5 * {x}7 / 365") for x in "EFGH"]
        row = ["A/P"] + balance_sheet.accounts_payable + forecast
        self._spreadsheet.append_row(row)

        # Accrued Expenses
        historical = balance_sheet.other_current_liabilities
        forecast = [FormulaCell(f"{x}6 * I23") for x in "EFGH"]
        percent_of_sales = [
            FormulaCell("sum([ B23 / B6 , C23 / C6 , D23 / D6 ]) / 3", Style.Percent)
        ]
        row = ["Accrued Expenses"] + historical + forecast + percent_of_sales
        self._spreadsheet.append_row(row)

        # Term Loan Current Portion
        row = (
            ["Term Loan Current Portion"]
            + balance_sheet.long_term_debt_current_portion
            + [20 for _ in range(4)]
        )
        self._spreadsheet.append_row(row)

        # Term Loan
        row = ["Term Loan"] + balance_sheet.long_term_debt + [80, 60, 40, 20]
        self._spreadsheet.append_row(row)

        # Net Worth
        forecast = [FormulaCell(f"{x}26 + {y}13") for x, y in zip("DEFG", "EFGH")]
        row = ["Net Worth"] + balance_sheet.share_holders_equity + forecast
        self._spreadsheet.append_row(row)

        # Total Liabilities
        row = ["Total Liabilities"] + [
            FormulaCell(
                f"sum([ {x}19 , {x}20 , {x}21 , {x}22 , {x}23 , {x}24 , {x}25 , {x}26 ])"
            )
            for x in "BCDEFGH"
        ]
        self._spreadsheet.append_row(row)

    def to_string(self, width: int = 5) -> str:
        return self._spreadsheet.to_string(width)

    def to_df(self):
        return self._spreadsheet.to_df(evaluate=False)
    
if __name__ == "__main__":
    company_id = 1

    income_statement = dao.load_income_statement(company_id)
    balance_sheet = dao.load_balance_sheet(company_id)

    ccc = CashConversionCycle(
        income_statement, 
        balance_sheet, 
        sales_growth=.25, 
        interest_rate=.05,
        num_forecast_cols=4
    )

    print(ccc.to_df())
