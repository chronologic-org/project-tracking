import streamlit as st
import pandas as pd
from typing import List, Optional, Tuple

def render_login_form() -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Render the login form and return the form submission status and credentials.
    
    Returns:
        Tuple[bool, Optional[str], Optional[str]]: A tuple containing:
            - bool: Whether the form was submitted
            - Optional[str]: Username if submitted
            - Optional[str]: Password if submitted
    """
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_submitted = st.form_submit_button("Login")
        
        if login_submitted:
            return True, username, password
    return False, None, None

def render_register_form() -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Render the registration form and return the form submission status and credentials.
    
    Returns:
        Tuple[bool, Optional[str], Optional[str]]: A tuple containing:
            - bool: Whether the form was submitted
            - Optional[str]: Username if submitted
            - Optional[str]: Password if submitted
    """
    with st.form("register_form"):
        st.subheader("Register New User")
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        register_submitted = st.form_submit_button("Register")
        
        if register_submitted:
            if new_password != confirm_password:
                st.error("Passwords do not match")
                return False, None, None
            elif not new_username or not new_password:
                st.error("Username and password are required")
                return False, None, None
            return True, new_username, new_password
    return False, None, None

def render_sidebar(current_user: str) -> str:
    """
    Render the sidebar navigation and return the selected page.
    
    Args:
        current_user (str): The username of the currently logged-in user.
        
    Returns:
        str: The selected page name.
    """
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Dashboard", "Projects", "Problems", "Categories", "Users", "Analytics", "Leaderboard"])
    
    st.sidebar.header("Current User")
    st.sidebar.write(f"Logged in as: {current_user}")
    
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.user_id = None
        st.session_state.session_token = None
        st.rerun()
    
    return page

def display_dataframe(df: pd.DataFrame, columns: Optional[List[str]] = None) -> None:
    """
    Display a DataFrame with optional column filtering.
    
    Args:
        df (pd.DataFrame): The DataFrame to display.
        columns (Optional[List[str]]): List of columns to display. If None, displays all columns.
    """
    if df.empty:
        st.info("No data available.")
        return
        
    if columns:
        st.dataframe(df[columns], use_container_width=True)
    else:
        st.dataframe(df, use_container_width=True)

def display_metrics(title: str, value: float, delta: Optional[float] = None) -> None:
    """
    Display a metric with optional delta value.
    
    Args:
        title (str): The metric title.
        value (float): The metric value.
        delta (Optional[float]): The delta value to display.
    """
    st.metric(title, value, delta=delta) 