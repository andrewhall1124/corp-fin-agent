import pandas as pd
import streamlit as st
import dao

from cash_conversion_cycle import CashConversionCycle

company_id = 1

income_statement = dao.load_income_statement(company_id)
balance_sheet = dao.load_balance_sheet(company_id)

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
