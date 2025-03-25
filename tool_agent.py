from smolagents import CodeAgent, HfApiModel, TransformersModel  # noqa: F401
from dotenv import load_dotenv
import os
import polars as pl
from smolagents import tool

# Read in csv file
df = pl.read_csv("financial_statements_clean.csv")


@tool
def get_variable_names() -> list[str]:
    """
    This is a tool that returns the list of available variable names.
    It returns the list of variable names.
    """
    return df["item"].to_list()


@tool
def get_available_years() -> list[int]:
    """
    This is a tool that returns the list of available years in the database.
    It returns the list of variable years.
    """
    return [int(year) for year in df.columns if year != "item"]


@tool
def historical_average(variable: str) -> float:
    """
    This is a tool that returns the historical average of a specified variable.
    It returns the average value of the variable.

    Args:
        variable: The variable in the database to look for.
    """
    return (
        df
        # Get mean value for specified column
        .filter(pl.col("item").eq(variable))
        .unpivot(index="item", variable_name="year")  
        ["value"]
        .mean()
    )


@tool
def get_variable_by_year(variable: str, year: int) -> float:
    """
    This is a tool that returns the value of a specified variable for a specified year.
    It returns the value for that year.

    Args:
        variable: The variable in the database to look for.
        year: The year in the database to look for.
    """
    return (
        df
        # Get the last value for a specified variable and year
        .filter(pl.col("item").eq(variable))
        .unpivot(index="item", variable_name="year")
        .cast({"year": pl.Int32})
        .filter(pl.col("year").eq(year))["value"]
        .last()
    )


@tool
def forecast_value_with_growth_rate(
    initial_value: float, growth_rate: float, periods: int
) -> list[float]:
    """
    This is a tool that returns a forecast of values based on an initial value and a growth rate.
    It returns a list of future values.

    Args:
        initial_value: The first value to beging the forecast with.
        growth_rate: The rate at which the value grows in decimal format.
        periods: The number of periods to forecast for
    """
    result = []
    for i in range(periods):
        if i == 0:
            next_value = initial_value * (1 + growth_rate)
            result.append(next_value)
        else:
            next_value = result[-1] * (1 + growth_rate)
            result.append(next_value)

    return result


@tool
def historical_percent_of_sales(variable: str) -> float:
    """
    This is a tool that returns the historical percent of sales of a specified variable.
    It returns the decimal format ammount of the variable as a percentage of sales.

    Args:
        variable: The variable in the database to look for.
    """
    return (
        df
        # Get average percent of salse
        .filter(pl.col("item").is_in(["sales", variable]))
        .unpivot(index="item", variable_name="year")
        .pivot(index="year", on="item")
        .with_columns((pl.col(variable) / pl.col("sales")).alias("percent"))["percent"]
        .mean()
    )


@tool
def forecast_interest_expense(
    previous_year_short_term_debt: float,
    previous_year_long_term_debt: float,
    short_term_interest_rate: float,
    long_term_interest_rate: float,
) -> float:
    """
    This is a tool that returns the forecasted interest expense using last years long term
    and short term debt values, and the forecasted short term and long term interest rates.
    It returns the forecasted interest expense.

    Args:
        previous_year_short_term_debt: The previous years short term debt.
        previous_year_long_term_debt: The previous years long term debt.
        short_term_interest_rate: The forecasted short term interest rate.
        long_term_interest_rate: The forecasted long term interest rate.

    """
    return (
        previous_year_short_term_debt * short_term_interest_rate
        + previous_year_long_term_debt * long_term_interest_rate
    )


load_dotenv(override=True)
token = os.getenv("HF_INFERENCE_API_TOKEN")

model_id = "Qwen/Qwen2.5-Coder-32B-Instruct"
model = HfApiModel(model_id=model_id, token=token)

# model_id = "meta-llama/Llama-3.2-1B-Instruct"
# model = TransformersModel(model_id, device_map='mps', max_new_tokens=4096)

agent = CodeAgent(
    tools=[
        historical_average,
        get_variable_names,
        get_available_years,
        get_variable_by_year,
        forecast_value_with_growth_rate,
        historical_percent_of_sales,
        forecast_interest_expense,
    ],
    model=model,
    add_base_tools=False,
)

# --- FORECAST KEY ASSUMPTIONS ---

# # Sales Growth
# sales_growth_rate = agent.run(
#     "What is 2007 sales growth rate? Forecast it as an average of the previous years.",
# )  # 22.022%
sales_growth_rate = .22022

# # Taxes
# tax_rate = agent.run(
#     "What is 2007's tax rate? Forecast it as an average of the previous years.",
# ) # 42.767%
tax_rate = .42767

# # Dividend Payout
# dividend_payout_rate = agent.run(
#     "What is 2007's dividend payout rate? Forecast it as an average of the previous years.",
# ) # 37.550%
dividend_payout_rate = .37550

# # Short Term Interest Rate
# short_term_interest_rate = agent.run(
#     "What is 2007's short term interest rate? Forecast it as last years value.",
# ) # 7.150%
short_term_interest_rate = 0.0715

# # Long Term Interest Rate
# long_term_interest_rate = agent.run(
#     "What is 2007's long term interest rate? Forecast it as last years value.",
# ) # 5.960%
long_term_interest_rate = 0.0596

# --- Forecast sales ---
# sales = agent.run(
#     f"Forecast sales for 2007 using last years sales and the growth rate: {sales_growth_rate * 100:.3f}%.",
# )  # 113.508
sales = 113.508

# Forecast percent of sales items
# cost_of_goods_sold = agent.run(
#     f"Forecast cost of goods sold for 2007 using percent of sales forcasting given that 2007's sales are: ${sales}.",
# )  # 72.802
cost_of_goods_sold = 72.802

# sales_general_and_administrative_expenses = agent.run(
#     f"Forecast sales general and administrative costs for 2007 using percent of sales forcasting given that 2007's sales are: ${sales}.",
# )  # 8.529
sales_general_and_administrative_expenses = 8.259

# depreciation_expense = agent.run(
#     f"Forecast depreciation expense for 2007 using percent of sales forcasting given that 2007's sales are: ${sales}.",
# )  # 7.657
depreciation_expense = 7.657

# cash = agent.run(
#     f"Forecast cash for 2007 using percent of sales forcasting given that 2007's sales are: ${sales}.",
# )  # 7.481
cash = 7.481

# accounts_recievables = agent.run(
#     f"Forecast accounts recievables for 2007 using percent of sales forcasting given that 2007's sales are: ${sales}.",
# )  # 28.578
accounts_recievables = 28.578

# inventory = agent.run(
#     f"Forecast inventory for 2007 using percent of sales forcasting given that 2007's sales are: ${sales}.",
# )  # 36.137
inventory = 36.137

# property_plant_and_equipment = agent.run(
#     f"Forecast property plant and equipment for 2007 using percent of sales forcasting given that 2007's sales are: ${sales}.",
# )  # 503.26
property_plant_and_equipment = 503.26

# # Forecast accumulated_depreciation
# accumulated_depreciation = agent.run(
#     f"What is 2007's accumulated depreciation if 2007s depreciation expense is: ${depreciation_expense:.3f}.",
# ) # 89.571
accumulated_depreciation = 89.571

# accounts_payables = agent.run(
#     f"Forecast accounts payable for 2007 using percent of sales forcasting given that 2007's sales are: ${sales}.",
# )  # 78.819
accounts_payables = 78.819

# short_term_debt = agent.run(
#     f"Forecast short term debt for 2007 using percent of sales forcasting given that 2007's sales are: ${sales}.",
# )  # 60.281
short_term_debt = 60.281

# # Forecast interest expense
# interest_expense = agent.run(
#     f"""
#     Forecast interest expense for 2007 using the previous years short term and long term debt,
#     our forecast for 2007's short term interest rate ({short_term_interest_rate * 100:.3f}%),
#     and our forecast for 2007's long term interest rate ({long_term_interest_rate * 100:.3f}%)
#     """
# )  # 6.724
interest_expense = 6.724

# Section totals
ebit = sales - cost_of_goods_sold - sales_general_and_administrative_expenses - depreciation_expense

pretax_income = ebit - interest_expense

taxes = pretax_income * tax_rate

net_income = pretax_income - taxes

dividends = net_income * dividend_payout_rate

addition_to_retained_earnings = net_income - dividends

total_current_assets = cash + accounts_recievables + inventory

net_ppe = property_plant_and_equipment - accumulated_depreciation

total_current_liabilities = short_term_debt + accounts_payables



# # Forecast paid in capital
# paid_in_capital = agent.run(
#     "What is 2007's paid_in_capital? Forecast it as last years value.",
# ) # 147.40
paid_in_capital = 147.80

# # Forecast retained earnings
# retained_earnings = agent.run(
#     f"What is 2007's retained earnings if 2007s addition to retained earnings is: ${addition_to_retained_earnings:.3f}.",
# ) # 80.259
retained_earnings = 80.529


total_assets = net_ppe + total_current_assets
total_equity = paid_in_capital + retained_earnings

# Calculate the plug
long_term_debt = total_assets - total_equity - total_current_liabilities

print(f"Total financing needed: {long_term_debt}")  # 113.92