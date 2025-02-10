import sqlite3 as sql

with sql.connect("database/company_financials.db") as con:
    cursor = con.cursor()

    company_core_table = """
    CREATE TABLE IF NOT EXISTS company (
        id INTEGER PRIMARY  KEY AUTOINCREMENT,
        name TEXT
    );
    """

    cursor.execute(company_core_table)
    con.commit()

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

    cursor.execute(is_core_table)
    con.commit()

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
        propery_plant_and_equipment REAL,
        -- total assets
        accounts_payable REAL,
        short_term_debt REAL,
        long_term_debt_current_portion REAL,
        other_current_liabilities REAL,
        -- total current liabilities
        long_term_debt REAL,
        -- total liabilities
        share_holders_equity REAL,
        -- total equity
        PRIMARY KEY (company_id, year)
    );
    """

    cursor.execute(bs_core_table)
    con.commit()