import sqlite3 as sql
import pandas as pd

COMPANY_ID = 1
TABLE_NAME = 'clarkson_bs'
STG_TABLE = TABLE_NAME + "_stg"
XF_TABLE = TABLE_NAME + "_xf" 

# Import raw
df = pd.read_csv('data/clarkson_bs.csv')

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
with sql.connect('database/company_financials.db') as con:
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
            ap AS accounts_payable,
            notes_payable_bank_plug + note_payable_to_holtz + notes_payable_trade AS short_term_debt,
            term_loan_current_portion AS long_term_debt_current_portion,
            accrued_expenses AS other_current_liabilities,
            term_loan AS long_term_debt,
            net_worth AS share_holders_equity
        FROM {STG_TABLE}
    ;
    """

    cursor.execute(xf_query)
    con.commit()

    # Merge
    merge_query = f"""
    INSERT OR REPLACE INTO balance_sheet(
        company_id,
        year,
        cash,
        accounts_recievable,
        inventory,
        propery_plant_and_equipment,
        accounts_payable,
        short_term_debt,
        long_term_debt_current_portion,
        other_current_liabilities,
        long_term_debt,
        share_holders_equity
    )
    SELECT
        company_id,
        year,
        cash,
        accounts_recievable,
        inventory,
        propery_plant_and_equipment,
        accounts_payable,
        short_term_debt,
        long_term_debt_current_portion,
        other_current_liabilities,
        long_term_debt,
        share_holders_equity
    FROM {XF_TABLE}
    ;
    """

    cursor.execute(merge_query)
    con.commit()

    # Drop stage and transform tables
    drop_query = f"""
        DROP TABLE IF EXISTS {STG_TABLE};
    """

    cursor.execute(drop_query)
    con.commit()

    drop_query = f"""
        DROP TABLE IF EXISTS {XF_TABLE};
    """

    cursor.execute(drop_query)
    con.commit()

