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


def get_data(value_name: str) -> str:
    return df.select(["year", value_name]).write_json()


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

# Forecast interest expense

# Forecast dividends

# Forecast depreciation

# Calculate the plug
