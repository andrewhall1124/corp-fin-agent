from smolagents import HfApiModel, CodeAgent
from dotenv import load_dotenv
import os
import polars as pl
import random
import prompts
from tools import tool_box
import json


class AgentEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "dict") and callable(obj.dict):
            return obj.dict()
        if hasattr(obj, "to_dict") and callable(obj.to_dict):
            return obj.to_dict()
        if hasattr(obj, "__dict__"):
            return obj.__dict__
        return str(obj)


load_dotenv(override=True)

token = os.getenv("HF_INFERENCE_API_TOKEN")
model_id = "Qwen/Qwen2.5-Coder-32B-Instruct"
model = HfApiModel(model_id=model_id, token=token)

true_sales_growth_rate = 0.2202
true_sales = 113.51
true_cogs = 72.80


def evaluate(
    sales_growth_rate: float, sales: float, cost_of_goods_sold: float
) -> tuple[float]:
    """Return a list of errors."""
    true_sales_growth_rate = 0.2202
    true_sales = 113.51
    true_cogs = 72.80

    sgr_sse = (true_sales_growth_rate - round(sales_growth_rate, 4)) ** 2
    sales_sse = (true_sales - round(sales, 2)) ** 2
    cogs_sse = (true_cogs - round(cost_of_goods_sold, 2)) ** 2

    return sgr_sse, sales_sse, cogs_sse


# ---------- Workflow test ----------


def test_workflow(tools: bool, n_trials: int) -> pl.DataFrame:
    with_data = not tools

    for _ in range(n_trials):
        trial_int = random.randint(10000, 99999)

        if tools:
            workflow = CodeAgent(tools=tool_box, model=model, add_base_tools=False)
            name = "tools_workflow"

        else:
            workflow = CodeAgent(tools=[], model=model, add_base_tools=False)
            name = "no_tools_workflow"

        sales_growth_rate = workflow.run(
            task=prompts.sales_growth_rate_prompt(with_data)
        )

        sgr_steps = len(workflow.memory.steps)

        sales = workflow.run(task=prompts.sales_prompt(sales_growth_rate, with_data))

        sales_steps = len(workflow.memory.steps)

        cost_of_goods_sold = workflow.run(
            task=prompts.cost_of_goods_sold_prompt(sales, with_data)
        )

        cogs_steps = len(workflow.memory.steps)

        # Save memory
        steps = workflow.memory.get_full_steps()
        with open(f"results/logs/{name}_{trial_int}.json", "w") as f:
            json.dump(steps, f, indent=4, cls=AgentEncoder)

        sgr_sse, sales_sse, cogs_sse = evaluate(
            sales_growth_rate, sales, cost_of_goods_sold
        )

        results = [
            {
                "trial": trial_int,
                "agent": name,
                "task": "sales_growth_rate",
                "predicted_value": sales_growth_rate,
                "steps": sgr_steps,
                "error": sgr_sse,
            },
            {
                "trial": trial_int,
                "agent": name,
                "task": "sales",
                "predicted_value": sales,
                "steps": sales_steps,
                "error": sales_sse,
            },
            {
                "trial": trial_int,
                "agent": name,
                "task": "cost_of_goods_sold",
                "predicted_value": cost_of_goods_sold,
                "steps": cogs_steps,
                "error": cogs_sse,
            },
        ]

        results_df = pl.from_dicts(results)
        results_df.write_csv(f"results/{name}_{trial_int}.csv")
        print(results_df)


# ---------- Agent test ----------


def test_agent(tools: bool, n_trials: int) -> pl.DataFrame:
    with_data = not tools

    for _ in range(n_trials):
        trial_int = random.randint(10000, 99999)

        if tools:
            agent = CodeAgent(tools=tool_box, model=model, add_base_tools=False)
            name = "tools_agent"

        else:
            agent = CodeAgent(tools=[], model=model, add_base_tools=False)
            name = "no_tools_agent"

        result = agent.run(task=prompts.full_prompt(with_data))

        sales_growth_rate = result["sales_growth_rate"]
        sales = result["sales"]
        cost_of_goods_sold = result["cost_of_goods_sold"]

        n_steps = len(agent.memory.steps)

        # Save memory
        steps = agent.memory.get_full_steps()
        with open(f"results/logs/{name}_{trial_int}.json", "w") as f:
            json.dump(steps, f, indent=4, cls=AgentEncoder)

        sgr_sse, sales_sse, cogs_sse = evaluate(
            sales_growth_rate, sales, cost_of_goods_sold
        )

        results = [
            {
                "trial": trial_int,
                "agent": name,
                "task": "sales_growth_rate",
                "predicted_value": sales_growth_rate,
                "steps": n_steps / 3,
                "error": sgr_sse,
            },
            {
                "trial": trial_int,
                "agent": name,
                "task": "sales",
                "predicted_value": sales,
                "steps": n_steps / 3,
                "error": sales_sse,
            },
            {
                "trial": trial_int,
                "agent": name,
                "task": "cost_of_goods_sold",
                "predicted_value": cost_of_goods_sold,
                "steps": n_steps / 3,
                "error": cogs_sse,
            },
        ]

        results_df = pl.from_dicts(results)
        results_df.write_csv(f"results/{name}_{trial_int}.csv")
        print(results_df)


if __name__ == "__main__":
    os.makedirs("results", exist_ok=True)
    os.makedirs("results/logs", exist_ok=True)

    # Tests
    test_workflow(tools=True, n_trials=1)
    test_workflow(tools=False, n_trials=1)
    test_agent(tools=True, n_trials=1)
    test_agent(tools=False, n_trials=1)
