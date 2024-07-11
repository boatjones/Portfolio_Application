import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# open credential yaml file
with open("security.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

# create authenticator object with yaml contents
authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
    config["preauthorized"],
)

# login user details from object
# name, authentication_status, username = authenticator.login("Login", "main")  <== deprecated form_name
#login user details from object
fields = {"username": "Username", "password": "Password"}
name, authentication_status, username = authenticator.login("main", fields=fields)
# submit_button = st.form_submit_button(label='Login')

# successful login section
if st.session_state["authentication_status"]:
    authenticator.logout("Logout", "main")
    st.write(f'Welcome *{st.session_state["name"]}*')

    # post authentication home/start page for application
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

# unsuccessful login section
elif st.session_state["authentication_status"] == False:
    st.error("Username/password is incorrect")
elif st.session_state["authentication_status"] == None:
    st.warning("Please enter your username and password")
