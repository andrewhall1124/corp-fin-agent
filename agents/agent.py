from smolagents import HfApiModel, CodeAgent, TransformersModel
from dotenv import load_dotenv
import os
import polars as pl
import utils
import random

load_dotenv(override=True)

TOKEN = os.getenv("HF_INFERENCE_API_TOKEN")
MODEL_ID = "Qwen/Qwen2.5-Coder-32B-Instruct"
MODEL = HfApiModel(model_id=MODEL_ID, token=TOKEN)

# model_id = "Qwen/Qwen2.5-Coder-0.5B-Instruct"
# model = TransformersModel(model_id=model_id)

TRUE_SALES_GROWTH_RATE = .2202
TRUE_SALES = 113.51
TRUS_COGS = 72.80

TOOLS = []

def full_prompt(with_data: bool) -> str:
    prompt = (
"""
Forecast cost of goods sold for 2007 using percent of sales forecasting methods. 
First calculate 2007 sales growth as a average of historical sales growth.
Second calculate 2007 sales as a function of 2007 sales growth.
Third calculate cost of goods sold as a percent of 2007 sales.
"""
    )

    if with_data:
        prompt += (
f"""
Data: 
{utils.get_data(['sales_growth_rate', 'sales', 'cost_of_goods_sold'])}
"""
        )

    return prompt


def sales_growth_rate_prompt(with_data: bool) -> str:
    prompt = (
"""
What is 2007 sales growth rate? Forecast it as an average of the previous years.
"""
    )

    if with_data:
        prompt += (
f"""
Data:
{utils.get_data('sales_growth_rate')}
"""
        )

    return prompt


def sales_prompt(sales_growth_rate: float, with_data: bool) -> str:
    prompt = (
f"""
Forecast sales for 2007 using last years sales and the growth rate: {sales_growth_rate*100}%.
"""
    )

    if with_data:
        prompt += (
f"""
Data:
{utils.get_data('sales')}
"""
        )

    return prompt


def cost_of_goods_sold_prompt(sales: float, with_data: bool) -> str:
    prompt = (
f"""
Forecast Cost of Goods Sold for 2007 using percent of sales forcasting given that the previous years' sales is: {sales}.
"""
    )

    if with_data:
        prompt += (
f"""
Data:
{utils.get_data(['sales', 'cost_of_goods_sold'])}
"""
        )
    
    return prompt

# ---------- No tools workflow ----------

def test_workflow(tools: bool, n_trials: int) -> pl.DataFrame:
    with_data = not tools

    for _ in range(n_trials):
        trial_int = random.randint(10000, 99999)

        if tools:
            workflow = CodeAgent(tools=TOOLS, model=MODEL, add_base_tools=False)
            name = 'tools_workflow'

        else:
            workflow = CodeAgent(tools=[], model=MODEL, add_base_tools=False)
            name = 'no_tools_workflow'

        sales_growth_rate = workflow.run(
            task=sales_growth_rate_prompt(with_data)
        )

        sgr_steps = len(workflow.memory.steps)

        sales = workflow.run(
            task=sales_prompt(sales_growth_rate, with_data)
        )

        sales_steps = len(workflow.memory.steps)

        cost_of_goods_sold = workflow.run(
            task=cost_of_goods_sold_prompt(sales, with_data)
        )

        cogs_steps = len(workflow.memory.steps)

        def evaluate(sales_growth_rate: float, sales: float, cost_of_goods_sold: float) -> tuple[float]:
            """Return a list of accuracies."""

            sgr_sse = (TRUE_SALES_GROWTH_RATE - round(sales_growth_rate, 4)) ** 2
            sales_sse = (TRUE_SALES - round(sales, 2)) ** 2
            cogs_sse = (TRUS_COGS - round(cost_of_goods_sold, 2)) ** 2

            return sgr_sse, sales_sse, cogs_sse

        sgr_sse, sales_sse, cogs_sse = evaluate(sales_growth_rate, sales, cost_of_goods_sold)

        results = [
            {
                'trial': trial_int,
                'agent': name,
                'task': 'sales_growth_rate',
                'steps': sgr_steps,
                'error': sgr_sse,
            },
            {
                'trial': trial_int,
                'agent': name,
                'task': 'sales',
                'steps': sales_steps,
                'error': sales_sse,
            },
            {
                'trial': trial_int,
                'agent': name,
                'task': 'cost_of_goods_sold',
                'steps': cogs_steps,
                'error': cogs_sse,
            },
        ]

        results_df = pl.from_dicts(results)
        results_df.write_csv(f"results/{name}_{trial_int}.csv")
        print(results_df)

if __name__ == "__main__":
    os.makedirs("results")
    test_workflow(tools=False, n_trials=1)
        
