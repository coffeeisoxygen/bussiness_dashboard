import streamlit as st

from config.logging import setup_logging

setup_logging()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


def login():
    """Handle user login.

    This function checks if the login button is pressed and updates the session state accordingly.
    """
    if st.button("Log in"):
        st.session_state.logged_in = True
        st.rerun()


def logout():
    """Handle user logout.

    This function checks if the logout button is pressed and updates the session state accordingly.
    """
    if st.button("Log out"):
        st.session_state.logged_in = False
        st.rerun()


login_page = st.Page(login, title="Log in", icon=":material/login:")
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")

dashboard = st.Page(
    "pages/reports/dashboard.py",
    title="Dashboard",
    icon=":material/dashboard:",
    default=True,
)

transaction = st.Page(
    "pages/reports/transactions.py", title="Transactions", icon=":material/autoplay:"
)

rgu = st.Page(
    "pages/reports/rgu.py", title="RGU", icon=":material/receipt_long:"
)  # RGU stands for Revenue Generating Unit

sellin = st.Page("pages/reports/sellin.py", title="Sell-in", icon=":material/sync_alt:")

tertiery = st.Page(
    "pages/reports/tertiery.py", title="Tertiary", icon=":material/star:"
)

retailer = st.Page(
    "pages/masters/retailer.py", title="Retailer", icon=":material/receipt_long:"
)

desa = st.Page("pages/masters/desa.py", title="Desa", icon=":material/home:")

site = st.Page("pages/masters/site.py", title="Site", icon=":material/cell_tower:")

file_upload = st.Page(
    "pages/tools/file_upload.py", title="File Upload", icon=":material/file_upload:"
)
if st.session_state.logged_in:
    pg = st.navigation(
        {
            "Account": [logout_page],
            "Reports": [dashboard, transaction, rgu, sellin, tertiery],
            "Master": [retailer, site, desa],
            "Tools": [file_upload],
        }
    )
else:
    pg = st.navigation([login_page])

pg.run()
