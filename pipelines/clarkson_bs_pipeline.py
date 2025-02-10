import sqlite3 as sql
import pandas as pd

COMPANY_ID = 1
TABLE_NAME = 'clarkson_bs'
STG_TABLE = TABLE_NAME + "_stg"
XF_TABLE = TABLE_NAME + "_xf" 

# Import raw
df = pd.read_csv('clarkson_bs.csv')

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

    # Stage table
    df.to_sql(
        name=STG_TABLE,
        con=con,
        if_exists='replace',
        index=False
    )

    # Drop existing transform table
    drop_query = f"""
        DROP TABLE IF EXISTS {XF_TABLE};
    """

    cursor.execute(drop_query)
    con.commit()

    # Transform Table
    xf_query = f"""
    CREATE TABLE {XF_TABLE} AS 
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

    cursor.execute(xf_query)
    con.commit()
