import dao
import string

from spreadsheet import FormulaCell, SpreadSheet, Style, ValueCell
from statements import IncomeStatement, BalanceSheet

R = {
    "sales_growth": 3,
    "interest_rate": 4,
    "tax_rate": 5,
    "payables_period": 8,
    "recievables_period": 9,
    "inventory_period": 10,
    "ccc": 11,
    "net_sales": 14,
    "cost_of_goods_sold": 15,
    "gross_profit": 16,
    "operating_expense": 18,
    "operating_income": 19,
    "interest_expense": 21,
    "ebt": 22,
    "taxes": 24,
    "net_income": 25,
    "cash": 28,
    "accounts_receivable": 29,
    "inventory": 30,
    "total_current_assets": 31,
    "property_plant_and_equipment": 33,
    "total_assets": 34,
    "short_term_debt": 36,
    "accounts_payable": 37,
    "long_term_debt_current_portion": 38,
    "other_short_term_liabilities": 39,
    "total_current_liabilities": 40,
    "long_term_debt": 42,
    "total_liabilities": 43,
    "shareholders_equity": 45,
    "total_liabilities_and_equity": 46,
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
        self._num_historical_cols = len(income_statement.year)

        forecast_years = [
            max(historical_years) + i for i in range(1, num_forecast_cols + 1)
        ]
        self._num_forecast_cols = num_forecast_cols
        years = sorted(historical_years) + sorted(forecast_years)

        total_columns = 2 + self._num_historical_cols + self._num_forecast_cols
        self._columns = string.ascii_uppercase[0:total_columns]

        # Common columns
        self._historical_cols = self._columns[1 : 1 + self._num_historical_cols]
        self._percent_of_sales_col = self._columns[
            1 + self._num_historical_cols + self._num_forecast_cols
        ]
        self._forecast_cols = self._columns[
            1 + self._num_historical_cols : 1
            + self._num_historical_cols
            + self._num_forecast_cols
        ]
        self._spreadsheet = SpreadSheet(0, total_columns)
        self._header(years)
        self._key_assumptions(sales_growth, interest_rate)
        self._cash_conversion_cycle()
        self._income_statement(income_statement)
        self._balance_sheet(balance_sheet)

    def _header(self, years):
        # Year headers
        row = ["Year"] + [str(year) for year in years] + ["Percent of Sales"]
        self._spreadsheet.append_row(row)

        # Column Sub Headers
        row = (
            ["Item"]
            + ["Actual" for _ in range(self._num_historical_cols)]
            + ["Forecast" for _ in range(self._num_forecast_cols)]
        )
        self._spreadsheet.append_row(row)

    def _key_assumptions(self, sales_growth: float, interest_rate: float):
        # Section Header
        row = ["Key Assumptions"]
        self._spreadsheet.append_row(row)

        # Sales Growth
        columns_1 = self._columns[1 : self._num_historical_cols]
        columns_2 = self._columns[2 : 1 + self._num_historical_cols]

        historical = [None] + [
            FormulaCell(
                f"( {y}{R['net_sales']} - {x}{R['net_sales']} ) / {x}{R['net_sales']}",
                Style.Percent,
            )
            for x, y in zip(columns_1, columns_2)
        ]
        forecast = [
            ValueCell(sales_growth, Style.Percent)
            for _ in range(self._num_forecast_cols)
        ]
        row = ["Sales Growth"] + historical + forecast
        self._spreadsheet.append_row(row)

        # Interest Rate
        row = (
            ["Interest Rate"]
            + [None for _ in range(3)]
            + [
                ValueCell(interest_rate, Style.Percent)
                for _ in range(self._num_forecast_cols)
            ]
        )
        self._spreadsheet.append_row(row)

        # Tax Rate
        columns = self._columns[
            self._num_historical_cols : self._num_historical_cols
            + self._num_forecast_cols
        ]
        historical = [
            FormulaCell(f"{x}{R['taxes']} / {x}{R['ebt']}", Style.Percent)
            for x in self._historical_cols
        ]
        forecast = [FormulaCell(f"{x}{R['tax_rate']}", Style.Percent) for x in columns]
        row = ["Tax Rate"] + historical + forecast
        self._spreadsheet.append_row(row)

        # Blank Row
        self._spreadsheet.append_row([])

    def _cash_conversion_cycle(self):
        row = ["Cash Conversion Cycle"]
        self._spreadsheet.append_row(row)

        # Payables Period
        columns = self._columns[
            self._num_historical_cols : self._num_historical_cols
            + self._num_forecast_cols
        ]
        historical = [
            FormulaCell(
                f"( {x}{R['accounts_payable']} / ( {x}{R['cost_of_goods_sold']} / 365 ))"
            )
            for x in self._historical_cols
        ]
        forecast = [FormulaCell(f"{x}{R['payables_period']}") for x in columns]
        row = ["Payables Period"] + historical + forecast
        self._spreadsheet.append_row(row)

        # Receivables Period
        historical = [
            FormulaCell(
                f"( {x}{R['accounts_receivable']} / ( {x}{R['cost_of_goods_sold']} / 365 ))"
            )
            for x in [*self._historical_cols, *self._forecast_cols]
        ]
        row = ["Receivables Period"] + historical
        self._spreadsheet.append_row(row)

        # Inventory Period
        historical = [
            FormulaCell(f"( {x}{R['inventory']} / ( {x}{R['net_sales']} / 365 ))")
            for x in [*self._historical_cols, *self._forecast_cols]
        ]
        row = ["Inventory Period"] + historical
        self._spreadsheet.append_row(row)

        # CCC
        historical = [
            FormulaCell(
                f"( {x}{R['inventory_period']} + {x}{R['recievables_period']} - {x}{R['payables_period']} )"
            )
            for x in [*self._historical_cols, *self._forecast_cols]
        ]
        row = ["CCC"] + historical
        self._spreadsheet.append_row(row)

        # Blank Row
        self._spreadsheet.append_row([])

    def _income_statement(self, income_statement: IncomeStatement):
        row = ["Income Statement"]
        self._spreadsheet.append_row(row)

        # Net Sales
        columns = self._columns[
            self._num_historical_cols : self._num_historical_cols
            + self._num_forecast_cols
        ]
        historical = income_statement.net_sales
        forecast = [FormulaCell(f"( {x}{R['net_sales']} * ( {y}{R['sales_growth']} + 1 ))") for x, y in zip(columns, self._forecast_cols)]
        row = ["Net Sales"] + historical + forecast
        self._spreadsheet.append_row(row)

        # COGS
        historical = income_statement.cost_of_goods_sold
        forecast = [FormulaCell(f"( {x}{R['net_sales']} * {self._percent_of_sales_col}15 )") for x in self._forecast_cols]
        ratios = " , ".join(
            [
                f"{col}{R['cost_of_goods_sold']} / {col}{R['net_sales']}"
                for col in self._historical_cols
            ]
        )
        percent_of_sales = [
            FormulaCell(
                f"sum([ {ratios} ]) / {self._num_historical_cols}", Style.Percent
            )
        ]
        row = ["COGS"] + historical + forecast + percent_of_sales
        self._spreadsheet.append_row(row)

        # Gross Profit
        historical = [FormulaCell(f"( {x}{R['net_sales']} - {x}{R['cost_of_goods_sold']} )") for x in [*self._historical_cols, *self._forecast_cols]]
        row = ["Gross Profit"] + historical
        self._spreadsheet.append_row(row)

        # Blank Row
        self._spreadsheet.append_row([])

        # Operating Expense
        historical = income_statement.operating_expense
        forecast = [FormulaCell(f"( {x}{R['net_sales']} * {self._percent_of_sales_col}{R['operating_expense']} )") for x in self._forecast_cols]
        ratios = " , ".join(
            [
                f"{col}{R['operating_expense']} / {col}{R['net_sales']}"
                for col in self._historical_cols
            ]
        )
        percent_of_sales = [
            FormulaCell(
                f"sum([ {ratios} ]) / {self._num_historical_cols}", Style.Percent
            )
        ]
        row = ["Operating Expense"] + historical + forecast + percent_of_sales
        self._spreadsheet.append_row(row)

        # Operating Income (EBIT)
        historical = [FormulaCell(f"( {x}{R['gross_profit']} - {x}{R['operating_expense']} )") for x in [*self._historical_cols, *self._forecast_cols]]
        row = ["Operating Income (EBIT)"] + historical
        self._spreadsheet.append_row(row)

        # Blank Row
        self._spreadsheet.append_row([])

        # Interest Expense
        historical = income_statement.interest_expense
        columns = self._columns[
            self._num_historical_cols : self._num_historical_cols
            + self._num_forecast_cols
        ]
        forecast = [FormulaCell(f"( {x}{R['short_term_debt']} * {y}{R['interest_rate']} )") for x, y in zip(columns, self._forecast_cols)]
        row = ["Interest Expense"] + historical + forecast
        self._spreadsheet.append_row(row)

        # Pre-tax Income (EBT)
        historical = [FormulaCell(f"( {x}{R['operating_income']} - {x}{R['interest_expense']} )") for x in [*self._historical_cols, *self._forecast_cols]]
        row = ["Pre-tax Income (EBT)"] + historical
        self._spreadsheet.append_row(row)

        # Blank Row
        self._spreadsheet.append_row([])

        # Taxes
        historical = income_statement.taxes
        forecast = [FormulaCell(f"( {x}{R['ebt']} * {x}{R['tax_rate']} )") for x in self._forecast_cols]
        row = ["Taxes"] + historical + forecast
        self._spreadsheet.append_row(row)

        # Net Income
        historical = [FormulaCell(f"( {x}{R['ebt']} - {x}{R['taxes']} )") for x in [*self._historical_cols, *self._forecast_cols]]
        row = ["Net Income"] + historical
        self._spreadsheet.append_row(row)

        # Blank Row
        self._spreadsheet.append_row([])


    def _balance_sheet(self, balance_sheet: BalanceSheet):
        row = ["Balance Sheet"]
        self._spreadsheet.append_row(row)
        
        # Cash
        historical = balance_sheet.cash
        ratios = " , ".join(
            [
                f"{col}{R['cash']} / {col}{R['net_sales']}"
                for col in self._historical_cols
            ]
        )
        percent_of_sales = [
            FormulaCell(
                f"sum([ {ratios} ]) / {self._num_historical_cols}", Style.Percent
            )
        ]
        forecast = [
            FormulaCell(
                f"{x}{R['net_sales']} * {self._percent_of_sales_col}{R['cash']}"
            )
            for x in self._forecast_cols
        ]
        row = ["Cash"] + historical + forecast + percent_of_sales
        self._spreadsheet.append_row(row)

        # Accounts Receivable
        historical = balance_sheet.accounts_recievable
        forecast = [
            FormulaCell(f"{x}{R['net_sales']} * {self._percent_of_sales_col}{R['accounts_receivable']}")
            for x in self._forecast_cols
        ]
        ratios = " , ".join(
            [
                f"{col}{R['accounts_receivable']} / {col}{R['net_sales']}"
                for col in self._historical_cols
            ]
        )
        percent_of_sales = [
            FormulaCell(
                f"sum([ {ratios} ]) / {self._num_historical_cols}", Style.Percent
            )
        ]
        row = ["Accounts Receivables"] + historical + forecast + percent_of_sales
        self._spreadsheet.append_row(row)

        # Inventory
        historical = balance_sheet.inventory
        forecast = [
            FormulaCell(
                f"{x}{R['net_sales']} * {self._percent_of_sales_col}{R['inventory']}"
            )
            for x in self._forecast_cols
        ]
        ratios = " , ".join(
            [
                f"{col}{R['inventory']} / {col}{R['net_sales']}"
                for col in self._historical_cols
            ]
        )
        percent_of_sales = [
            FormulaCell(
                f"sum([ {ratios} ]) / {self._num_historical_cols}", Style.Percent
            )
        ]
        row = ["Inventory"] + historical + forecast + percent_of_sales
        self._spreadsheet.append_row(row)

        # Total Current Assets
        row = ["Total Current Assets"] + [
            FormulaCell(
                f"sum([ {x}{R['cash']} , {x}{R['accounts_receivable']} , {x}{R['inventory']} ])"
            )
            for x in [*self._historical_cols, *self._forecast_cols]
        ]
        self._spreadsheet.append_row(row)

        # Blank Row
        self._spreadsheet.append_row([])

        # Property Plant and Equipment
        historical = balance_sheet.property_plant_and_equipment
        forecast = [
            FormulaCell(
                f"{x}{R['net_sales']} * {self._percent_of_sales_col}{R['property_plant_and_equipment']}"
            )
            for x in self._forecast_cols
        ]
        ratios = " , ".join(
            [
                f"{col}{R['property_plant_and_equipment']} / {col}{R['property_plant_and_equipment']}"
                for col in self._historical_cols
            ]
        )
        percent_of_sales = [
            FormulaCell(
                f"sum([ {ratios} ]) / {self._num_historical_cols}", Style.Percent
            )
        ]
        row = (
            ["Property Plant and Equipment"] + historical + forecast + percent_of_sales
        )
        self._spreadsheet.append_row(row)

        # Total Assets
        row = ["Total Assets"] + [
            FormulaCell(
                f"{x}{R['total_current_assets']} + {x}{R['property_plant_and_equipment']}"
            )
            for x in [*self._historical_cols, *self._forecast_cols]
        ]
        self._spreadsheet.append_row(row)

        # Blank Row
        self._spreadsheet.append_row([])

        # Short Term Debt (PLUG)
        historical = balance_sheet.short_term_debt
        forecast = [
            FormulaCell(
                f"{x}{R['total_assets']} - sum([ {x}{R['accounts_payable']} , {x}{R['long_term_debt_current_portion']} , {x}{R['other_short_term_liabilities']} , {x}{R['long_term_debt']} , {x}{R['shareholders_equity']} ])"
            )
            for x in self._forecast_cols
        ]
        row = ["Short Term Debt (PLUG)"] + historical + forecast
        self._spreadsheet.append_row(row)

        # Accounts Payable
        forecast = [FormulaCell(f"{x}{R['payables_period']} * {x}{R['cost_of_goods_sold']} / 365") for x in self._forecast_cols]
        row = ["Accounts Payable"] + balance_sheet.accounts_payable + forecast
        self._spreadsheet.append_row(row)

        # Long Term Debt Current Portion
        row = (
            ["Long Term Debt Current Portion"]
            + balance_sheet.long_term_debt_current_portion
            + [20 for _ in range(4)]  # TODO: Fix
        )
        self._spreadsheet.append_row(row)

        # Other Short Term Liabilities
        historical = balance_sheet.other_current_liabilities
        forecast = [0 for _ in self._forecast_cols]
        row = ["Other Short Term Liabilities"] + historical + forecast
        self._spreadsheet.append_row(row)

        # Total Current Liabilities
        row = ["Total Current Liabilities"] + [
            FormulaCell(
                f"{x}{R['short_term_debt']} + {x}{R['accounts_payable']} + {x}{R['long_term_debt_current_portion']} + {x}{R['other_short_term_liabilities']}"
            )
            for x in [*self._historical_cols, *self._forecast_cols]
        ]
        self._spreadsheet.append_row(row)

        # Blank Row
        self._spreadsheet.append_row([])

        # Long Term Debt
        row = ["Long Term Debt"] + balance_sheet.long_term_debt + [80, 60, 40, 20]
        self._spreadsheet.append_row(row)

        # Total Liabilities
        row = ["Total Liabilities"] + [
            FormulaCell(
                f"{x}{R['total_current_liabilities']} + {x}{R['long_term_debt']}"
            )
            for x in [*self._historical_cols, *self._forecast_cols]
        ]
        self._spreadsheet.append_row(row)

        # Blank Row
        self._spreadsheet.append_row([])

        # Shareholders Equity
        columns = self._columns[
            self._num_historical_cols : self._num_historical_cols
            + self._num_forecast_cols
        ]
        forecast = [
            FormulaCell(f"{x}{R['shareholders_equity']} + {y}{R['net_income']}")
            for x, y in zip(columns, self._forecast_cols)
        ]
        row = ["Net Worth"] + balance_sheet.share_holders_equity + forecast
        self._spreadsheet.append_row(row)

        # Total Liabilities and Equity
        row = ["Total Liabilities and Equity"] + [
            FormulaCell(f"{x}{R['total_liabilities']} + {x}{R['shareholders_equity']}")
            for x in [*self._historical_cols, *self._forecast_cols]
        ]
        self._spreadsheet.append_row(row)

    def to_string(self, width: int = 5) -> str:
        return self._spreadsheet.to_string(width)

    def to_df(self):
        return self._spreadsheet.to_df()


if __name__ == "__main__":
    company_id = 1

    income_statement = dao.load_income_statement(company_id)
    balance_sheet = dao.load_balance_sheet(company_id)

    ccc = CashConversionCycle(
        income_statement,
        balance_sheet,
        sales_growth=0.25,
        interest_rate=0.05,
        num_forecast_cols=4,
    )

    print(ccc.to_df())
