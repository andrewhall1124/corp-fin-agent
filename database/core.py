

company_core_table = """
CREATE TABLE IF NOT EXISTS company (
    id INTEGER PRIMARY  KEY AUTOINCREMENT,
    name TEXT
);
"""

is_core_table = """
CREATE TABLE IF NOT EXISTS income_statement (
    -- ids
    company_id INTEGER,
    year INTEGER,
    -- income statement
    net_sales REAL,
    other_pre_profit_income REAL,
    cost_of_goods_sold REAL,
    other_pre_profit_expenses REAL,
    -- gross profit
    operating_expense REAL,
    -- operating income (EBIT)
    interest_expense REAL,
    -- pre-tax income (EBT)
    taxes REAL,
    -- net income
    PRIMARY KEY (company_id, year)
);
"""

bs_core_table = """
CREATE TABLE IF NOT EXISTS balance_sheet (
    -- ids
    company_id INTEGER,
    year INTEGER,
    -- balance sheet
    cash REAL,
    accounts_recievable REAL,
    inventory REAL,
    -- total non-current assets
    propery_plant_and_equipemtn REAL,
    -- total assets
    accounts_payable REAL,
    short_term_debt REAL,
    long_term_debt_current_portion REAL,
    -- total current liabilities
    other_current_liabilities REAL,
    long_term_debt REAL,
    -- total liabilities
    share_holders_equity REAL,
    -- total equity
    PRIMARY KEY (company_id, year)
);
"""