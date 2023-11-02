import pandas as pd
import numpy as np

# sys.path.insert(0, os.path.join(Path(__file__).parents[1]))
from to_postgres import PgHook

# make database helper object
db = PgHook()


def mc_hammer(port_list):
    # calculate the number of stocks in portfolio
    N = len(port_list)

    # retrieve price history for selected tickers
    columns = ", ".join(port_list)
    sql2 = f"select price_date, {columns} from prices"
    print(f"port select: {sql2}")
    port = db.alc_query(sql2)

    # set date to be index thus removing it from simulations
    port.set_index("price_date", inplace=True)

    ###### HELPER FUNCTIONS
    # make a function to generate random portfolio weights
    def gen_weights(N):
        weights = np.random.random(N)
        return weights / np.sum(weights)

    # make a function to calculate an annualized portfolio return given a certain
    # portfolio weighting
    def calculate_returns(weights, log_rets):
        # annualize return
        return np.sum(log_rets.mean() * weights) * 252

    # create a function to calculate volatility
    def calculate_volatility(weights, log_rets_cov):
        annualized_cov = np.dot(log_rets_cov * 252, weights)
        vol = np.dot(weights.transpose(), annualized_cov)
        return np.sqrt(vol)

    # calculating the variables needed for simulation
    log_rets = np.log(port / port.shift(1))
    log_rets_cov = log_rets.cov()

    """
        Monte Carlo Simulation of Input Tickers
    """
    # list to hold the returns from the monte carlo simulation
    mc_portfolio_returns = []
    mc_portfolio_vol = []
    mc_weights = []

    # note that the number of stocks in the portfolio makes the length of
    # the simulation grow exponentially in complexity
    for sim in range(6000):
        weights = gen_weights(N)
        mc_weights.append(weights)
        sim_returns = calculate_returns(weights, log_rets)
        mc_portfolio_returns.append(sim_returns)
        sim_volatility = calculate_volatility(weights, log_rets_cov)
        mc_portfolio_vol.append(sim_volatility)

    # assume zero risk-free rate to calculate Sharpe ratio
    mc_sharpe_ratios = np.array(mc_portfolio_returns / np.array(mc_portfolio_vol))

    # assemble dataframe of results
    df_weights = pd.DataFrame(np.row_stack(mc_weights))
    df_weights.columns = port_list

    df_portfolio_returns = pd.DataFrame(np.row_stack(mc_portfolio_returns))
    df_portfolio_returns.columns = ["return"]

    df_portfolio_vol = pd.DataFrame(np.row_stack(mc_portfolio_vol))
    df_portfolio_vol.columns = ["volatility"]

    df_portfolio_sharpe = pd.DataFrame(np.row_stack(mc_sharpe_ratios))
    df_portfolio_sharpe.columns = ["sharpe"]

    df_portfolio_mc = pd.concat(
        [df_weights, df_portfolio_returns, df_portfolio_vol, df_portfolio_sharpe],
        axis=1,
    )

    # sort dataframe descending by Sharpe ratio
    mc_final = df_portfolio_mc.sort_values("sharpe", ascending=False)

    return mc_final


def ndx_calc(mc_frame):
    # get first row that's been sorted by Sharpe Ratio
    weights = mc_frame.head(1)
    # put weights into a dictionary
    weights_dict = weights.to_dict(orient="records")[0] if not weights.empty else {}
    # List of keys to be removed
    keys_to_remove = ["return", "volatility", "sharpe"]

    # Removing specific key-value pairs from the dictionary
    for key in keys_to_remove:
        weights_dict.pop(key, None)

    # get list of tickers to work with
    port_list = list(weights_dict)

    # put them in a comma separated string
    columns = ", ".join(port_list)
    # use this to select just these tickers from table
    sql2 = f"select price_date, {columns} from log_returns"
    print(f"df select: {sql2}")
    log_returns_df = db.alc_query(sql2)

    # Calculate the daily portfolio value
    daily_portfolio_value = [100]  # Start with 100 on the earliest day

    for i in range(1, len(log_returns_df)):
        day_prices = daily_portfolio_value[-1]  # Get the previous day's prices
        current_day_portfolio_value = 0

        for ticker, weight in weights_dict.items():
            if ticker in log_returns_df.columns:
                log_return = log_returns_df.loc[i, ticker]
                if not pd.isnull(log_return):
                    current_day_portfolio_value += (
                        day_prices * (1 + log_return) * weight
                    )

        daily_portfolio_value.append(current_day_portfolio_value)

    # Create a DataFrame with 'price_date' and 'portfolio_value'
    result_df = pd.DataFrame(
        {
            "price_date": log_returns_df["price_date"],
            "portfolio_value": daily_portfolio_value,
        }
    )
    return result_df
