import streamlit as st

st.title("Portfolio Application")
st.text(
    """ 
    An application to evaluate a portfolio of stocks, create optimized indices,
    plot these indices against a signal commodity, calculate its correlation to 
    the indices and then apply elements of machine learning to predict future values.
    """
)

st.header("Here are the different pages to the application:")

st.subheader("Individual Historical Prices")
st.text(
    """
    Retrieves historical prices for all tickers in the portfolio plus the commodity, 
    stores them plus the log returns in a database for use in following studies, and 
    then charts the individual stock prices' returns segregated by sector.
    """
)

st.subheader("Monte Carlo Index Creation")
st.text(
    """
    Uses Monte Carlo simulation to create optimal porfolio allocations for each sector 
    and uses these allocations to create indices for the sectors.
    """
)

st.subheader("Correlation Studies")
st.text(
    """
    Calculates the correlation of each index against the commodity and charts a 
    heatmap of these correlations.
    """
)

st.subheader("Prediction and Sensitivity")
st.text(
    """
    Using a linear regression model, attempts to predict future performance of each 
    sector index based on commodity price movement.
    """
)
