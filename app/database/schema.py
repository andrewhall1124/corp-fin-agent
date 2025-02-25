from database import Database
import os
from pathlib import Path

with Database() as db:

    folder = Path("database/tables")
    for file in os.listdir(folder):
        
        with open(folder / file, 'r') as sql:
            db.execute(sql.read())
