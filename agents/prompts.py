"""Module for experiment prompts."""

import utils


def full_prompt(with_data: bool) -> str:
    prompt = """
Forecast cost of goods sold for 2007 using percent of sales forecasting methods. 
First calculate 2007 sales growth as a average of historical sales growth.
Second calculate 2007 sales as a function of 2007 sales growth.
Third calculate cost of goods sold as a percent of 2007 sales.

Return your forecast for 2007 sales growth rate, sales, and cost of goods sold
as a dictionary like this:
{
    "sales_growth_rate": 0.50,
    "sales": 150.45,
    "cost_of_goods_sold": 40.67,
}
"""

    if with_data:
        prompt += f"""
Data: 
{utils.get_data(['sales_growth_rate', 'sales', 'cost_of_goods_sold'])}
"""

    return prompt


def sales_growth_rate_prompt(with_data: bool) -> str:
    prompt = """
What is 2007 sales growth rate? Forecast it as an average of the previous years.
"""

    if with_data:
        prompt += f"""
Data:
{utils.get_data('sales_growth_rate')}
"""

    return prompt


def sales_prompt(sales_growth_rate: float, with_data: bool) -> str:
    prompt = f"""
Forecast sales for 2007 using last years sales and the growth rate: {sales_growth_rate*100}%.
"""

    if with_data:
        prompt += f"""
Data:
{utils.get_data('sales')}
"""

    return prompt


def cost_of_goods_sold_prompt(sales: float, with_data: bool) -> str:
    prompt = f"""
Forecast Cost of Goods Sold for 2007 using percent of sales forcasting given that the previous years' sales is: {sales}.
"""

    if with_data:
        prompt += f"""
Data:
{utils.get_data(['sales', 'cost_of_goods_sold'])}
"""

    return prompt
