from smolagents import HfApiModel, CodeAgent
from dotenv import load_dotenv
import os
import polars as pl

load_dotenv(override=True)
token = os.getenv("HF_INFERENCE_API_TOKEN")
model_id = "Qwen/Qwen2.5-Coder-32B-Instruct"

model = HfApiModel(model_id=model_id, token=token)
agent = CodeAgent(tools=[], model=model, add_base_tools=True)

# Read in csv file
df = pl.read_csv("financial_statements_clean.csv")
headers = df["value"].to_list()
df = df.drop("value").transpose(
    include_header=True, header_name="year", column_names=headers
)


def get_data(value_names: list[str]) -> str:
    if not isinstance(value_names, list):
        value_names = [value_names]
    return df.select(["year"] + value_names).write_json()


def clean_output(raw_output: any) -> float:
    if isinstance(raw_output, str):
        return float(raw_output.strip("%"))
    else:
        return raw_output


def prompt_llm(prompt: str, data_column_name: str) -> float:
    data = get_data(data_column_name)
    result = agent.run(prompt + f"\nData: {data}")
    return clean_output(result)



# --- FORECAST KEY ASSUMPTIONS ---

# Sales Growth
sales_growth_rate = prompt_llm(
    prompt="What is 2007 sales growth rate? Forecast it as an average of the previous years.",
    data_column_name="sales_growth_rate",
)
print("SALES_GROWTH_RATE", sales_growth_rate)

# Taxes
tax_rate = prompt_llm(
    prompt="What is 2007's tax rate? Forecast it as an average of the previous years.",
    data_column_name="tax_rate",
)
print("TAX_RATE", tax_rate)

# Dividend Payout
dividend_payout_rate = prompt_llm(
    prompt="What is 2007's dividend payout rate? Forecast it as an average of the previous years.",
    data_column_name="dividend_payout_rate",
)
print("DIVIDEND_PAYOUT_RATE", dividend_payout_rate)

# Short Term Interest Rate
short_term_interest_rate = prompt_llm(
    prompt="What is 2007's short term interest rate? Forecast it as last years value.",
    data_column_name="short_term_interest_rate",
)
print("SHORT_TERM_INTEREST_RATE", short_term_interest_rate)

# Long Term Interest Rate
long_term_interest_rate = prompt_llm(
    prompt="What is 2007's long term interest rate? Forecast it as last years value.",
    data_column_name="long_term_interest_rate",
)
print("LONG_TERM_INTEREST_RATE", long_term_interest_rate)

# --- Forecast sales ---
sales = prompt_llm(
    prompt=f"Forecast sales for 2007 using last years sales and the growth rate: {sales_growth_rate}%.",
    data_column_name='sales'
)
print("SALES", sales)


# Forecast percent of sales items
cost_of_goods_sold = prompt_llm(
    prompt=f"Return the Forecast as a single number for Cost of Goods Sold for 2007 using percent of sales forcasting given that this years' sales is: {sales}%.",
    data_column_name=['sales', 'cost_of_goods_sold']
)
print("COST_OF_GOODS_SOLD", cost_of_goods_sold)

sales_general_and_administrative_expenses = prompt_llm(
    prompt=f"Return the Forecast as a single number for Sales General and Administrative Expenses for 2007 using percent of sales forcasting given that this years' sales is: {sales}%.",
    data_column_name=['sales', 'sales_general_and_administrative_expenses']
)
print("SALES_GENERAL_AND_ADMINISTRATIVE_EXPENSES", sales_general_and_administrative_expenses)

depreciation = prompt_llm(
    prompt=f"Return the Forecast as a single number for Depretiation Expense for 2007 using percent of sales forcasting given that this years' sales is: {sales}%.",
    data_column_name=['sales', 'depreciation']
)
print("SALES_GENERAL_AND_ADMINISTRATIVE_EXPENSES", depreciation)

cash = prompt_llm(
    prompt=f"Return the Forecast as a single number for Cash and Cash Equivalents for 2007 using percent of sales forcasting given that this years' sales is: {sales}%.",
    data_column_name=['sales', 'cash']
)
print("CASH", cash)

accounts_recievables = prompt_llm(
    prompt=f"Return the Forecast as a single number for Accounts Recievables for 2007 using percent of sales forcasting given that this years' sales is: {sales}%.",
    data_column_name=['sales', 'accounts_recievables']
)
print("ACCOUNTS_RECIEVABLES", accounts_recievables)

inventory = prompt_llm(
    prompt=f"Return the Forecast as a single number for Inventories for 2007 using percent of sales forcasting given that this years' sales is: {sales}%.",
    data_column_name=['sales', 'inventory']
)
print("INVENTORY", inventory)

property_plant_and_equipment = prompt_llm(
    prompt=f"Return the Forecast as a single number for Property, Plant, and Equipment for 2007 using percent of sales forcasting given that this years' sales is: {sales}%.",
    data_column_name=['sales', 'property_plant_and_equipment']
)
print("PROPERTY_PLANT_AND_EQUIPMENT", property_plant_and_equipment)

accounts_payables = prompt_llm(
    prompt=f"Return the Forecast as a single number for Accounts Payables for 2007 using percent of sales forcasting given that this years' sales is: {sales}%.",
    data_column_name=['sales', 'accounts_payables']
)
print("ACCOUNTS_PAYABLES", accounts_payables)

short_term_debt = prompt_llm(
    prompt=f"Return the Forecast as a single number for Short Term Debt for 2007 using percent of sales forcasting given that this years' sales is: {sales}%.",
    data_column_name=['sales', 'short_term_debt']
)
print("SHORT_TERM_DEBT", short_term_debt)

# Calculate the plug

long_term_debt = prompt_llm(
    prompt=f"Return the Forecast as a single number for Long Term Debt for 2007 using calculations of that years' forecasted total assets minus forecasted total shareholders equity minus forecasted total current liabilities",
    data_column_name=['cash', 'accounts_recievables', 'inventory', 'net_ppe', 'paid_in_capital', 'retained_earnings', 'accounts_payables', 'short_term_debt']
)
print("LONG_TERM_DEBT", long_term_debt)

# Forecast interest expense

interest_expense = prompt_llm(
    prompt=f"Return the Forecast as a single number for Interest Expense for 2007 using the 2006 values of {short_term_debt}% multiplied by {short_term_interest_rate}% added to {long_term_debt}% multiplied by {long_term_interest_rate}%.",
    data_column_name=['interest_expense', 'short_term_interest_rate', 'long_term_interest_rate', 'short_term_debt', 'long_term_debt']
)
print("INTEREST_EXPENSE", interest_expense)

# Forecast dividends

dividends = prompt_llm(
    prompt=f"Return the Forecast as a single number for Dividends for 2007 using {dividend_payout_rate}% multiplied by the calculated forecast for Net Income)",
    data_column_name=['dividends', 'dividend_payout_rate', 'net_income']
)
print("DIVIDENDS", dividends)

