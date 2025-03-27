from smolagents import HfApiModel, CodeAgent, TransformersModel
from dotenv import load_dotenv
import os
import polars as pl
import utils

TRUE_SALES_GROWTH_RATE = .2202
TRUE_SALES = 113.51
TRUS_COGS = 72.80

load_dotenv(override=True)
token = os.getenv("HF_INFERENCE_API_TOKEN")

model_id = "Qwen/Qwen2.5-Coder-32B-Instruct"
model = HfApiModel(model_id=model_id, token=token)

# model_id = "Qwen/Qwen2.5-Coder-0.5B-Instruct"
# model = TransformersModel(model_id=model_id)

def full_prompt() -> str:
    return (
f"""
Forecast cost of goods sold for 2007 using percent of sales forecasting methods. 
First calculate 2007 sales growth as a average of historical sales growth.
Second calculate 2007 sales as a function of 2007 sales growth.
Third calculate cost of goods sold as a percent of 2007 sales.

Data: 
{utils.get_data(['sales_growth_rate', 'sales', 'cost_of_goods_sold'])}
"""
    )


def sales_growth_rate_prompt() -> str:
    return (
f"""
What is 2007 sales growth rate? Forecast it as an average of the previous years.

Data:
{utils.get_data('sales_growth_rate')}
"""
    )


def sales_prompt(sales_growth_rate: float) -> str:
    return (
f"""
Forecast sales for 2007 using last years sales and the growth rate: {sales_growth_rate*100}%.

Data:
{utils.get_data('sales')}
"""
    )


def cost_of_goods_sold_prompt(sales: float) -> str:
    return (
f"""
Forecast Cost of Goods Sold for 2007 using percent of sales forcasting given that the previous years' sales is: {sales}.

Data:
{utils.get_data(['sales', 'cost_of_goods_sold'])}
"""
    )

# ---------- No tools workflow ----------
no_tools_workflow = CodeAgent(tools=[], model=model, add_base_tools=False)

sales_growth_rate = no_tools_workflow.run(
    task=sales_growth_rate_prompt()
)

sgr_steps = len(no_tools_workflow.memory.steps)

sales = no_tools_workflow.run(
    task=sales_prompt(sales_growth_rate)
)

sales_steps = len(no_tools_workflow.memory.steps)

cost_of_goods_sold = no_tools_workflow.run(
    task=cost_of_goods_sold_prompt(sales)
)

cogs_steps = len(no_tools_workflow.memory.steps)

def evaluate(sales_growth_rate: float, sales: float, cost_of_goods_sold: float) -> tuple[float]:
    """Return a list of accuracies."""

    sgr_sse = (TRUE_SALES_GROWTH_RATE - round(sales_growth_rate, 4)) ** 2
    sales_sse = (TRUE_SALES - round(sales, 2)) ** 2
    cogs_sse = (TRUS_COGS - round(cost_of_goods_sold, 2)) ** 2

    return sgr_sse, sales_sse, cogs_sse

sgr_sse, sales_sse, cogs_sse = evaluate(sales_growth_rate, sales, cost_of_goods_sold)

results = [
    {
        'trial': 1,
        'agent': 'no_tools_workflow',
        'task': 'sales_growth_rate',
        'steps': sgr_steps,
        'error': sgr_sse,
    },
    {
        'trial': 1,
        'agent': 'no_tools_workflow',
        'task': 'sales',
        'steps': sales_steps,
        'error': sales_sse,
    },
    {
        'trial': 1,
        'agent': 'no_tools_workflow',
        'task': 'cost_of_goods_sold',
        'steps': cogs_steps,
        'error': cogs_sse,
    },
]

print(results)
print(pl.from_dicts(results))
