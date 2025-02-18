import pandas as pd
from database import Database

COMPANY_ID = 2
TABLE_NAME = "playtime_bs"
STG_TABLE = TABLE_NAME + "_stg"
XF_TABLE = TABLE_NAME + "_xf"

# Import raw
df = pd.read_csv("data/playtime_bs.csv")

# Rename columns
df["value"] = df["value"].str.lower()
df["value"] = df["value"].str.replace(" ", "_")
df["value"] = df["value"].str.replace(",", "")
df["value"] = df["value"].str.replace("’", "")
df["value"] = df["value"].str.replace("-", "_")

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
                cash,
                accounts_recievable,
                inventory,
                plant_and_equipment_net AS propery_plant_and_equipment,
                accounts_payable,
                notes_payable_bank AS short_term_debt,
                long_term_debt_current_portion,
                accrued_taxes,
                long_term_debt,
                shareholders_equity AS share_holders_equity
            FROM {STG_TABLE}
        ;
        """
    )

    # Merge
    db.execute(
        f"""
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
            accrued_taxes,
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
            accrued_taxes,
            long_term_debt,
            share_holders_equity
        FROM {XF_TABLE}
        ;
        """
    )

    # Drop stage and transform tables
    db.execute(f"DROP TABLE IF EXISTS {STG_TABLE};")
    db.execute(f"DROP TABLE IF EXISTS {XF_TABLE};")
