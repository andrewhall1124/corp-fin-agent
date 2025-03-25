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