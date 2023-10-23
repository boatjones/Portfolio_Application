from dotenv import load_dotenv
from os import getenv
import psycopg2
import pandas as pd
from sqlalchemy import create_engine


# Set up the engine to access the data.
engine = create_engine("postgresql://rthomas:talisman@localhost:5432/octane")

# Use a SQL query to find the answer to the above prompt.
sql = """
select * from sector
"""
# with engine.connect() as conn:
#    for row in conn.execute(sql):
#        print(f'The number of rows in the stores table are: {row[0]}')

df = pd.read_sql_query(sql, engine)

df.to_csv("test_out.csv")
