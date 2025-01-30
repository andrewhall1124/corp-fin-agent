from dataclasses import dataclass

import pandas as pd

from spreadsheet import FormulaCell, SpreadSheet, Style, ValueCell


@dataclass
class IncomeStatement:
    net_sales: float
    cogs: float
    discount: float
    operating_expense: float
    interest_expense: float
    taxes: float


class CashConversionCycle:

    def __init__(
        self,
        income_statement: dict[str, list[float]],
        balance_sheet: dict[str, list[float]],
        sales_growth: float,
        interest_rate: float,
    ) -> None:
        self._spreadsheet = SpreadSheet(0, 9)
        self._header()
        self._key_assumptions(sales_growth, interest_rate)
        self._cash_conversion_cycle()
        self._income_statement(income_statement)
        self._balance_sheet(balance_sheet)

    def _header(self):
        # Year headers
        row = (
            ["Year"] + [str(year) for year in range(1993, 2000)] + ["Percent of Sales"]
        )
        self._spreadsheet.append_row(row)

        # Column Sub Headers
        row = ["Type"] + ["Actual" for _ in range(3)] + ["Forecast" for _ in range(4)]
        self._spreadsheet.append_row(row)

    def _key_assumptions(self, sales_growth: float, interest_rate: float):
        # Sales Growth
        historical = [None] + [
            FormulaCell(f"( {y}6 - {x}6 ) / {x}6", Style.Percent)
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
        historical = [FormulaCell(f"{x}12 / {x}11", Style.Percent) for x in "BCD"]
        forecast = [FormulaCell(f"{x}4", Style.Percent) for x in "DEFG"]
        row = ["Tax Rate"] + historical + forecast
        self._spreadsheet.append_row(row)

    def _cash_conversion_cycle(self):
        # Payables Period
        historical = [FormulaCell(f"( {x}21 + {x}22 ) / ( {x}7 / 365 )") for x in "BCD"]
        forecast = [FormulaCell(f"{x}5") for x in "DEFG"]
        row = ["Payables Period"] + historical + forecast
        self._spreadsheet.append_row(row)

    def _income_statement(self, income_statement: dict[str, list[float]]):
        # Net Sales
        historical = income_statement["net_sales"]
        forecast = [FormulaCell(f"{x}6 * ( 1 + {y}2 )") for x, y in zip("DEFG", "EFGH")]
        row = ["Net Sales"] + historical + forecast
        self._spreadsheet.append_row(row)

        # Cogs
        historical = income_statement["cogs"]
        forecast = [FormulaCell(f"{x}6 * I7") for x in "EFGH"]
        percent_of_sales = [
            FormulaCell("sum([ B7 / B6 , C7 / C6 , D7 / D6 ]) / 3", Style.Percent)
        ]
        row = ["COGS"] + historical + forecast + percent_of_sales
        self._spreadsheet.append_row(row)

        # Discount (fix later)
        row = ["Discount"] + income_statement["discount"] + [0 for _ in range(4)]
        self._spreadsheet.append_row(row)

        # Operating Expense
        historical = income_statement["operating_expense"]
        forecast = [FormulaCell(f"{x}6 * I9") for x in "EFGH"]
        percent_of_sales = [
            FormulaCell("sum([ B9 / B6 , C9 / C6 , D9 / D6 ]) / 3", Style.Percent)
        ]
        row = ["Operating Expense"] + historical + forecast + percent_of_sales
        self._spreadsheet.append_row(row)

        # Interest Expense
        historical = income_statement["interest_expense"]
        forecast = [FormulaCell(f"{x}3 * {y}19") for x, y in zip("EFGH", "DEFG")]
        row = ["Interest Expense"] + historical + forecast
        self._spreadsheet.append_row(row)

        # Pretax profits
        row = ["Pretax Profits"] + [
            FormulaCell(f"{x}6 - {x}7 + {x}8 - {x}9 - {x}10") for x in "BCDEFGH"
        ]
        self._spreadsheet.append_row(row)

        # Taxes
        historical = income_statement["taxes"]
        forecast = [FormulaCell(f"{x}4 * {x}11") for x in "EFGH"]
        row = ["Taxes"] + historical + forecast
        self._spreadsheet.append_row(row)

        # Net income
        row = ["Net Income"] + [FormulaCell(f"{x}11 - {x}12") for x in "BCDEFGH"]
        self._spreadsheet.append_row(row)

    def _balance_sheet(self, balance_sheet: dict[str, list[float]]):
        # Cash
        historical = balance_sheet["cash"]
        forecast = [FormulaCell(f"{x}6 * I14") for x in "EFGH"]
        percent_of_sales = [
            FormulaCell("sum([ B14 / B6 , C14 / C6 , D14 / D6 ]) / 3", Style.Percent)
        ]
        row = ["Cash"] + historical + forecast + percent_of_sales
        self._spreadsheet.append_row(row)

        # A/R
        historical = balance_sheet["ar"]
        forecast = [FormulaCell(f"{x}6 * I15") for x in "EFGH"]
        percent_of_sales = [
            FormulaCell("sum([ B15 / B6 , C15 / C6 , D15 / D6 ]) / 3", Style.Percent)
        ]
        row = ["A/R"] + historical + forecast + percent_of_sales
        self._spreadsheet.append_row(row)

        # Inventory
        historical = balance_sheet["inventory"]
        forecast = [FormulaCell(f"{x}6 * I16") for x in "EFGH"]
        percent_of_sales = [
            FormulaCell("sum([ B16 / B6 , C16 / C6 , D16 / D6 ]) / 3", Style.Percent)
        ]
        row = ["Inventory"] + historical + forecast + percent_of_sales
        self._spreadsheet.append_row(row)

        # PP&E
        historical = balance_sheet["ppe"]
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
        historical = balance_sheet["notes_payable_bank_plug"]
        forecast = [
            FormulaCell(f"{x}18 - sum([ {x}22 , {x}23 , {x}24 , {x}25 , {x}26 ])")
            for x in "EFGH"
        ]
        row = ["Notes Payable (PLUG)"] + historical + forecast
        self._spreadsheet.append_row(row)

        # Notes Payable Holtz
        row = (
            ["Notes Payable Holtz"]
            + balance_sheet["note_payable_to_holtz"]
            + [0 for _ in range(4)]
        )
        self._spreadsheet.append_row(row)

        # Notes Payable Trade
        row = (
            ["Notes Payable Trade"]
            + balance_sheet["notes_payable_trade"]
            + [0 for _ in range(4)]
        )
        self._spreadsheet.append_row(row)

        # A/P
        forecast = [FormulaCell(f"{x}5 * {x}7 / 365") for x in "EFGH"]
        row = ["A/P"] + balance_sheet["ap"] + forecast
        self._spreadsheet.append_row(row)

        # Accrued Expenses
        historical = balance_sheet["accrued_expenses"]
        forecast = [FormulaCell(f"{x}6 * I23") for x in "EFGH"]
        percent_of_sales = [
            FormulaCell("sum([ B23 / B6 , C23 / C6 , D23 / D6 ]) / 3", Style.Percent)
        ]
        row = ["Accrued Expenses"] + historical + forecast + percent_of_sales
        self._spreadsheet.append_row(row)

        # Term Loan Current Portion
        row = (
            ["Term Loan Current Portion"]
            + balance_sheet["term_loan_current_portion"]
            + [20 for _ in range(4)]
        )
        self._spreadsheet.append_row(row)

        # Term Loan
        row = ["Term Loan"] + balance_sheet["term_loan"] + [80, 60, 40, 20]
        self._spreadsheet.append_row(row)

        # Net Worth
        forecast = [FormulaCell(f"{x}26 + {y}13") for x, y in zip("DEFG", "EFGH")]
        row = ["Net Worth"] + balance_sheet["net_worth"] + forecast
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
        return self._spreadsheet.to_df()
