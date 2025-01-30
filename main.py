import streamlit as st
import pandas as pd
from cash_conversion_cycle import CashConversionCycle

data = pd.read_csv("raw.csv")

# User can upload their own file
# uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
# if uploaded_file is not None:
#     data = pd.read_csv(uploaded_file)


# Rename columns
data["value"] = data["value"].str.lower()
data["value"] = data["value"].str.replace(" ", "_")
data["value"] = data["value"].str.replace("(", "")
data["value"] = data["value"].str.replace(")", "")
data["value"] = data["value"].str.replace("&", "")
data["value"] = data["value"].str.replace(",", "")
data["value"] = data["value"].str.replace("/", "")

data = data.set_index("value").T

income_statement = {
    "net_sales": data["net_sales"].to_list(),
    "cogs": data["cogs"].to_list(),
    "discount": data["discount"].to_list(),
    "operating_expense": data["operating_expense"].to_list(),
    "interest_expense": data["interest_expense"].to_list(),
    "taxes": data["taxes"].to_list(),
}


# Number input
# int(...) Converts the float to an integer immediately.
# step=1 Ensures only whole numbers can be selected.
# format="%d" Displays the number as an integer.
assumption = int(st.number_input("Enter assumption", step=1, format="%d"))


ccc = CashConversionCycle(income_statement=income_statement, assumption=assumption)

df = ccc.to_df()

# Remove row indices
# reset_index(inplace=True, drop=True)

# Coloring
st.title(":blue[Corporate Finance App]")
st.table(df)

# look into streamlit funcitonality: formatting, coloring, data types
