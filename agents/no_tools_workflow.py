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
headers = df["item"].to_list()
df = df.drop("item").transpose(
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

sales_growth_rate = prompt_llm(
    prompt="What is 2007 sales growth rate? Forecast it as an average of the previous years.",
    data_column_name=['sales_growth_rate']
)
print("SALES_GROWTH_RATE", sales_growth_rate)

sales = prompt_llm(
    prompt=f"Forecast sales for 2007 using last years sales and the growth rate: {sales_growth_rate*100}.",
    data_column_name=['sales', 'sales_growth_rate']
)
print("SALES", sales)

cost_of_goods_sold = prompt_llm(
    prompt=f"Forecast Cost of Goods Sold for 2007 using percent of sales forcasting given that the previous years' sales is: {sales}.",
    data_column_name=['sales', 'cost_of_goods_sold']
)
print("COST_OF_GOODS_SOLD", cost_of_goods_sold)
