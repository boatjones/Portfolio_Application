# Portfolio_Application
Apply various metrics to an equity portfolio storing data in a database.
A streamlit application to take an equity portfolio stored in an SQL database as a list of tickers segregated by
sectors and apply various metrics.  The current database used is PostgreSQL.  The application reads data from 
the database as well as creates tables on the database.  One motivation to storing data is to avoid multiple
duplicate retrievals via yfinance. This description will evolve as the application evolves itself.
