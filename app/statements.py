from dataclasses import dataclass


@dataclass
class BalanceSheet:
    year: int
    cash: float
    accounts_recievable: list[float]
    inventory: list[float]
    property_plant_and_equipment: list[float]
    accounts_payable: list[float]
    short_term_debt: list[float]
    long_term_debt_current_portion: list[float]
    other_current_liabilities: list[float]
    long_term_debt: list[float]
    share_holders_equity: list[float]


@dataclass
class IncomeStatement:
    year: list[int]
    net_sales: list[float]
    cost_of_goods_sold: list[float]
    operating_expense: list[float]
    interest_expense: list[float]
    taxes: list[float]
