# Portfolio_Application
Apply various metrics to an equity portfolio storing data in a database.
A streamlit application to take an equity portfolio stored in an SQL database as a list of tickers segregated by
sectors and apply various metrics.  The current database used is PostgreSQL.  The application reads data from 
the database as well as creates tables on the database.  One motivation to storing data is to avoid multiple
duplicate retrievals via yfinance. Thanks to this architecture, I used Python to dynamically create the SQL 
needed to source the data for the application at various points. 

The operative files in the application are

/src:

to_postgres.py - the file containing the Postgres helper class that handles queries and table creates

mc_core.py -

a. contains the function "mc_hammer" that takes a list of tickers along with a table of price history and runs a simulation of 6000 trials for varying portfolio weights to find the combinations of return and volatility.

b. contains the function "ndx_calc" that takes the best resulting Sharpe ratio of each simulation and constructs an index starting at 100 at the beginning price date and, according to the portfolio weights and the logrithmic returns, also stored in a table, to construce a price for this index over time.

a_Home.py - is the front page of the Streamlit application.

/src/pages:

b_Prices.py - 1) Allows the user to see the composition of the portfolio across the industry sectors. 2) Downloads a five year history of price data for all of the securities in the portfolio - including the commodity prices.  3) Allows the display of the logarithmic returns for securities in a selected segment over this time period.
   
c_MC_Simulation.py - 1) Performs a Monte Carlo simulation across the entire portfolio as well as the individual industry industry sectors.  These simulations are stored to a database table specific to each simulation.  Additionally, the indices based on the optimal weights in each portfolio by Sharpe ration are constructed and stored in an ndx_vals table.  2) By selection of industry segment, a chart of each simulation's results can be viewed.

d_Ndx_Correlation.py - 1) Charts each constructed industry index over time against the commodity price. 2) Calculates and charts a correlation matrix of these industry segments and the commodity.

Visual files used in the Streamlit application deliberately break Python naming conventions since they are also used as
menu pick items. 
