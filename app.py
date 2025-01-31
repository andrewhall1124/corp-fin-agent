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
st.set_page_config(layout="wide", page_title="Cashflow Conversion Cycle")

st.title("Cashflow Conversion Cycle")

col1, col2 = st.columns(2)

with col1:

    col1a, col1b = st.columns(2)

    st.subheader("Assumptions", divider="gray")

    with col1a:
        sales_growth = st.number_input("Sales Growth (%)", value=25)

    with col1b:
        interest_rate = st.number_input("Interest Rate (%)", value=11)

ccc = CashConversionCycle(
    income_statement=income_statement,
    balance_sheet=balance_sheet,
    sales_growth=sales_growth / 100,
    interest_rate=interest_rate / 100,
)

st.table(ccc.to_df())
