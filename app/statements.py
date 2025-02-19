from dataclasses import dataclass


@dataclass
class BalanceSheet:
    year: int
    cash: float
    accounts_recievable: float
    inventory: float
    property_plant_and_equipment: float
    accounts_payable: float
    short_term_debt: float
    long_term_debt_current_portion: float
    other_current_liabilities: float
    long_term_debt: float
    share_holders_equity: float


@dataclass
class IncomeStatement:
    year: list[int]
    net_sales: list[float]
    cost_of_goods_sold: list[float]
    operating_expense: list[float]
    interest_expense: list[float]
    taxes: list[float]
