import pandas as pd
import streamlit as st

from cash_conversion_cycle import CashConversionCycle


def process_data(df: pd.DataFrame) -> pd.DataFrame:
    # Rename columns
    df["value"] = df["value"].str.lower()
    df["value"] = df["value"].str.replace(" ", "_")
    df["value"] = df["value"].str.replace("(", "")
    df["value"] = df["value"].str.replace(")", "")
    df["value"] = df["value"].str.replace("&", "")
    df["value"] = df["value"].str.replace(",", "")
    df["value"] = df["value"].str.replace("/", "")

    # Transpose
    df = df.set_index("value").T

    return df


data = pd.read_csv("clarkson.csv")

data = process_data(data)

income_statement = {
    "net_sales": data["net_sales"].to_list(),
    "cogs": data["cogs"].to_list(),
    "discount": data["discount"].to_list(),
    "operating_expense": data["operating_expense"].to_list(),
    "interest_expense": data["interest_expense"].to_list(),
    "taxes": data["taxes"].to_list(),
}

balance_sheet = {
    "cash": data["cash"].to_list(),
    "ar": data["ar"].to_list(),
    "inventory": data["inventory"].to_list(),
    "ppe": data["ppe"].to_list(),
    "notes_payable_bank_plug": data["notes_payable_bank_plug"].to_list(),
    "note_payable_to_holtz": data["note_payable_to_holtz"].to_list(),
    "notes_payable_trade": data["notes_payable_trade"].to_list(),
    "ap": data["ap"].to_list(),
    "accrued_expenses": data["accrued_expenses"].to_list(),
    "term_loan_current_portion": data["term_loan_current_portion"].to_list(),
    "term_loan": data["term_loan"].to_list(),
    "net_worth": data["net_worth"].to_list(),
}

ccc = CashConversionCycle(
    income_statement=income_statement,
    balance_sheet=balance_sheet,
    sales_growth=0.25,
    interest_rate=0.11,
)

st.title("Cashflow Conversion Cycle")
# Two assumption inputs.
# Fix narrow formatting.
st.table(ccc.to_df())
