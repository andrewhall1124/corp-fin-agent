import sqlite3 as sql
import pandas as pd

COMPANY_NAME = 'clarkson'
COMPANY_ID = 1
STG_TABLE = COMPANY_NAME + "_stg" # Stage Table

IS_TABLE = COMPANY_NAME + "_is_xf"
BS_TABLE = COMPANY_NAME + "_bs_xf"

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

# Import raw
df = pd.read_csv('clarkson.csv')

# Rename columns
df["value"] = df["value"].str.lower()
df["value"] = df["value"].str.replace(" ", "_")
df["value"] = df["value"].str.replace("(", "")
df["value"] = df["value"].str.replace(")", "")
df["value"] = df["value"].str.replace("&", "")
df["value"] = df["value"].str.replace(",", "")
df["value"] = df["value"].str.replace("/", "")
df = df.rename(columns={'value': 'year'})

# Set index
df = df.set_index('year')

# Transpose
df = df.T.reset_index(names='year')

# SQL Queries
with sql.connect('company_financials.db') as con:
    cursor = con.cursor()

    # Stage
    df.to_sql(
        name=STG_TABLE,
        con=con,
        if_exists='replace',
        index=False
    )

    # Drop table
    drop_is_query = f"""
        DROP TABLE IF EXISTS {IS_TABLE};
    """

    cursor.execute(drop_is_query)
    con.commit()

    # Income statment table
    is_query = f"""
    CREATE TABLE {IS_TABLE} AS 
        SELECT
            {COMPANY_ID} AS company_id,
            year,
            net_sales,
            cogs AS cost_of_goods_sold,
            operating_expense,
            interest_expense,
            taxes
        FROM {STG_TABLE}
    ;
    """

    cursor.execute(is_query)
    con.commit()

    # Drop table
    drop_bs_query = f"""
        DROP TABLE IF EXISTS {BS_TABLE};
    """

    cursor.execute(drop_bs_query)
    con.commit()

    # Balance sheet table
    bs_query = f"""
    CREATE TABLE {BS_TABLE} AS 
        SELECT
            {COMPANY_ID} AS company_id,
            year,
            cash,
            ar AS accounts_recievable,
            inventory,
            ppe AS propery_plant_and_equipment,
            notes_payable_bank_plug + note_payable_to_holtz + notes_payable_trade AS short_term_debt,
            ap AS accounts_payable,
            accrued_expenses AS other_current_liabilities,
            term_loan_current_portion AS long_term_debt_current_portion,
            term_loan AS long_term_debt,
            net_worth AS share_holders_equity
        FROM {STG_TABLE}
    ;
    """

    cursor.execute(bs_query)
    con.commit()

# Index(['year', 'net_sales', 'cogs', 'discount', 'operating_expense',
#        'interest_expense', 'taxes', 'cash', 'ar', 'inventory', 'ppe',
#        'notes_payable_bank_plug', 'note_payable_to_holtz',
#        'notes_payable_trade', 'ap', 'accrued_expenses',
#        'term_loan_current_portion', 'term_loan', 'net_worth'],
#       dtype='object', name='year')

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
    -- total current liabilities
    other_current_liabilities REAL,
    long_term_debt REAL,
    -- total liabilities
    share_holders_equity REAL,
    -- total equity
    PRIMARY KEY (company_id, year)
);
"""