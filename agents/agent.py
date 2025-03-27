from smolagents import HfApiModel, CodeAgent, TransformersModel
from dotenv import load_dotenv
import os
import polars as pl

load_dotenv(override=True)
token = os.getenv("HF_INFERENCE_API_TOKEN")
# model_id = "Qwen/Qwen2.5-Coder-32B-Instruct"
model_id = "Qwen/Qwen2.5-Coder-0.5B-Instruct"


# model = HfApiModel(model_id=model_id, token=token)
model = TransformersModel(model_id=model_id, token=token)
agent = CodeAgent(tools=[], model=model, add_base_tools=True)

# ---------- Data ----------

# Read in csv file
df = pl.read_csv("financial_statements_clean.csv")
headers = df["item"].to_list()
df = df.drop("item").transpose(
    include_header=True, header_name="year", column_names=headers
)

def get_data(value_names: list[str]) -> str:
    if not isinstance(value_names, list):
        value_names = [value_names]
    return df.select(["year"] + value_names).write_json()

data = get_data(['sales_growth_rate', 'sales', 'cost_of_goods_sold'])


prompt = f"""
Forecast cost of goods sold for 2007 using percent of sales forecasting methods. 
First calculate 2007 sales growth as a average of historical sales growth.
Second calculate 2007 sales as a function of 2007 sales growth.
Third calculate cost of goods sold as a percent of 2007 sales.

Data: 
{data}
"""

print(prompt)