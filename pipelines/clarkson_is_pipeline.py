import sqlite3 as sql
import pandas as pd

COMPANY_ID = 1
TABLE_NAME = 'clarkson_is'
STG_TABLE = TABLE_NAME + "_stg"
XF_TABLE = TABLE_NAME + "_xf" 

# Import raw
df = pd.read_csv('data/clarkson_is.csv')

# Rename columns
df["value"] = df["value"].str.lower()
df["value"] = df["value"].str.replace(" ", "_")
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

    # Drop transform table
    drop_query = f"""
        DROP TABLE IF EXISTS {XF_TABLE};
    """

    cursor.execute(drop_query)
    con.commit()

    # Transform table
    xf_query = f"""
    CREATE TABLE {XF_TABLE} AS 
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

    cursor.execute(xf_query)
    con.commit()

    # Merge
    merge_query = f"""
    INSERT OR REPLACE INTO income_statement(
        company_id,
        year,
        net_sales,
        cost_of_goods_sold,
        operating_expense,
        interest_expense,
        taxes
    )
    SELECT
        company_id,
        year,
        net_sales,
        cost_of_goods_sold,
        operating_expense,
        interest_expense,
        taxes
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
