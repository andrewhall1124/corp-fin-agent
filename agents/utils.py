import polars as pl

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
