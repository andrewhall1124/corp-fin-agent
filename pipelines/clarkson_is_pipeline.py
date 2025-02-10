import sqlite3 as sql
import pandas as pd
from database import Database

COMPANY_ID = 1
TABLE_NAME = "clarkson_is"
STG_TABLE = TABLE_NAME + "_stg"
XF_TABLE = TABLE_NAME + "_xf"

# Import raw
df = pd.read_csv("data/clarkson_is.csv")

# Rename columns
df["value"] = df["value"].str.lower()
df["value"] = df["value"].str.replace(" ", "_")
df = df.rename(columns={"value": "year"})

# Set index
df = df.set_index("year")

# Transpose
df = df.T.reset_index(names="year")

# SQL Queries
with Database() as db:
    # Stage table
    db.load_df(df=df, table=STG_TABLE, replace=True, index=False)

    # Drop existing transform table
    db.execute(f"DROP TABLE IF EXISTS {XF_TABLE};")

    # Transform Table
    db.execute(
        f"""
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
    )

    # Merge
    db.execute(
        f"""
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
    )

    # Drop stage and transform tables
    db.execute(f"DROP TABLE IF EXISTS {STG_TABLE};")
    db.execute(f"DROP TABLE IF EXISTS {XF_TABLE};")
