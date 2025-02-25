import pandas as pd
import streamlit as st
import dao
from cash_conversion_cycle import CashConversionCycle

st.set_page_config(layout="wide", page_title="Cashflow Conversion Cycle")
st.title("Cashflow Conversion Cycle")

col1, col2 = st.columns(2)

with col1:
    col1a, col1b, col1c = st.columns(3)
    
    company_options = {
        "Clarkson": 1,
        "Playtime": 2,
    }
    
    with col1a:
        sales_growth = st.number_input("Sales Growth (%)", value=25)
    with col1b:
        interest_rate = st.number_input("Interest Rate (%)", value=11)
    with col1c:
        selected_company = st.selectbox("Select Company", options=list(company_options.keys()))
        company_id = company_options[selected_company]

income_statement = dao.load_income_statement(company_id)
balance_sheet = dao.load_balance_sheet(company_id)

ccc = CashConversionCycle(
    income_statement,
    balance_sheet,
    sales_growth=sales_growth / 100,
    interest_rate=interest_rate / 100,
    num_forecast_cols=4,
)

df = ccc.to_df()

def highlight_cells(df):
    highlighted = pd.DataFrame('', index=df.index, columns=df.columns)
    
    # Highlight section headers with light gray, black text, and underline
    header_rows = [2, 7, 13, 27]
    for row in header_rows:
        for col in df.columns:
            highlighted.loc[row, col] = 'background-color: #666666; color: black; border-bottom: 2px solid black'
    
    # Highlight goal cells with amber
    for row in range(8, 12):
        for col in ['E', 'F', 'G', 'H']:
            highlighted.loc[row, col] = 'background-color: rgba(255, 193, 7, 0.3)'
    
    return highlighted

styled_df = df.style.apply(highlight_cells, axis=None)
st.dataframe(styled_df, use_container_width=True)
