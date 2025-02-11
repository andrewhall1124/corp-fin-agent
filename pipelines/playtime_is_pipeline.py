import pandas as pd
from database.database import Database
from pathlib import Path

file_path = Path("data/playtime_is.csv") # Relative path
file_name = file_path.stem

COMPANY_ID = 2
TABLE_NAME = file_name
STG_TABLE = TABLE_NAME + "_stg"
XF_TABLE = TABLE_NAME + "_xf"

# Import raw
df = pd.read_csv(file_path)

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
                NULL AS other_pre_profit_income,
                cogs AS cost_of_goods_sold,
                NULL AS other_pre_profit_expenses,
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
            other_pre_profit_income,
            cost_of_goods_sold,
            other_pre_profit_expenses,
            operating_expense,
            interest_expense,
            taxes
        )
        SELECT
            company_id,
            year,
            net_sales,
            other_pre_profit_income,
            cost_of_goods_sold,
            other_pre_profit_expenses,
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
