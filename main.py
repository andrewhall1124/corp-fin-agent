from dataclasses import dataclass


@dataclass
class HistoricalData:
    interest_rate: list[float]
    wacc: float
    net_sales: list[float]
    cogs: list[float]
    discount: list[float]
    operating_expense: list[float]
    interest_expense: list[float]
    taxes: list[float]
    cash: list[float]
    ar: list[float]
    inventory: list[float]
    ppne: list[float]
    np_bank: list[float]
    np_holtz: list[float]
    np_trade: list[float]
    ap: list[float]
    accrued_expenses: list[float]
    term_loan_current_portion: list[float]
    term_loan: list[float]
    net_worth: list[float]


@dataclass
class ForecastAssumptions:
    sales_growth: list[float]
    interest_rate: list[float]
    payables_period: list[float]
    net_sales: float


class SpreadSheet:

    def __init__(self, data: HistoricalData, assumptions: ForecastAssumptions) -> None:
        # Do a bunch of magic
        plug: list[float] = None
        return plug


if __name__ == "__main__":
    data = HistoricalData(
        interest_rate=[11.0, 11.0, 0],
        wacc=10.0,
        net_sales=[2921.0, 3477.0, 4519.0],
        cogs=[2202.0, 2634.0, 3, 424],
        discount=[0.0, 0.0, 0.0],
        operating_expense=[622.0, 717.0, 940.0],
        interest_expense=[23.0, 42.0, 56.0],
        taxes=[14.0, 16.0, 22.0],
        cash=[43.0, 52.0, 56.0],
        ar=[306.0, 411.0, 606.0],
        inventory=[337.0, 432.0, 587.0],
        ppne=[233.0, 262.0, 388.0],
        np_bank=[0.0, 60.0, 390.0],
        np_holtz=[0.0, 200.0, 100.0],
        np_trade=[0.0, 0.0, 127.0],
        ap=[213.0, 340.0, 376.0],
        accrued_expenses=[42.0, 45.0, 75.0],
        term_loan_current_portion=[20.0, 20.0, 20.0],
        term_loan=[140.0, 120, 0, 100.0],
        net_worth=[504.0, 372.0, 449.0],
    )

    assumptions = ForecastAssumptions(
        sales_growth=[None, 25.0, 25.0, 25.0],
        interest_rate=[11.0, 11.0, 11.0, 11.0],
        payables_period=[53.6, 53.6, 53.6, 53.6],
        net_sales=5500.0,
    )

    sheet = SpreadSheet(
        data=data,
        assumptions=assumptions
    )
