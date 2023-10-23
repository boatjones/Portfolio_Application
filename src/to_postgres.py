from dotenv import load_dotenv
from os import getenv
import psycopg2
import pandas as pd
from sqlalchemy import create_engine


class PgHook:
    def __init__(self):
        load_dotenv()
        self.__pgurl = getenv("POSTGRES_URL")
        self.__user = getenv("LOCAL_USER")
        self.__pword = getenv("LOCAL_PASSWORD")

    def psy_query(self, sql):
        # open database connection
        conn = psycopg2.connect(
            dbname="octane", user=self.__user, password=self.__pword
        )
        # open database cursor
        cur = conn.cursor()
        cur.execute(sql)

        # get results to list
        result = cur.fetchall()
        # get column names for query result
        col_names = [desc[0] for desc in cur.description]
        # make dataframe of results with column names
        df = pd.DataFrame(result, columns=col_names)
        # close connection to the database
        cur.close()
        conn.close()
        return df

    def alc_query(self, sql):
        engine = create_engine(self.__pgurl)
        return pd.read_sql_query(sql, engine)

    def alc_df_2_db(self, in_df, tablename):
        engine = create_engine(self.__pgurl)
        # load dataframe to test table
        in_df.to_sql(tablename, engine, if_exists="replace", index=True)
