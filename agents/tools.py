from smolagents import tool
import polars as pl

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
def forecast_as_historical_average(variable: str) -> float:
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
        .unpivot(index="item", variable_name="year")["value"]
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
def forecast_percent_of_sales(variable: str) -> float:
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


tool_box = [
    get_variable_names,
    get_available_years,
    get_variable_by_year,
    forecast_as_historical_average,
    forecast_value_with_growth_rate,
    forecast_percent_of_sales,
]
