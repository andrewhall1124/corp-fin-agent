import sqlite3 as sql
import pandas as pd


class Database:
    def __init__(self, database_path="database/company_financials.db") -> None:
        self._database = database_path
        self._connection: sql.Connection = None
        self._cursor: sql.Cursor = None

    def __enter__(self) -> "Database":
        self._connection = sql.connect(self._database)
        self._cursor = self._connection.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self._cursor.close()
        self._connection.close()

    def load_df(
        self, df: pd.DataFrame, table: str, replace: bool = False, index: bool = True
    ) -> None:
        df.to_sql(
            name=table,
            con=self._connection,
            if_exists="replace" if replace else "fail",
            index=index,
        )

    def execute(self, query: str, parameters: tuple = ()):
        cursor = self._cursor.execute(query, parameters)
        self._connection.commit()
        return cursor.fetchall()
