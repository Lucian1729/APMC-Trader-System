# app/main.py
import streamlit as st
from authentication import authenticate_user
from utils import get_menu_options, show_user_menu
import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access variables using os.getenv
db_host = os.getenv("DB_HOST")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASS")
db_database = os.getenv("DB_NAME")

# Connect to MySQL database
def create_connection():
    return mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_database
    )

# Function to execute SQL queries
def execute_query(connection, query):
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()

# Function to fetch data from MySQL
def fetch_data(connection, query):
    cursor = connection.cursor()
    cursor.execute(query)
    return cursor.fetchall()


# Streamlit UI
def main():

    st.set_page_config(
    page_title="APMC Trader System",
    page_icon="🌾",
    layout="wide",
    )
    
    st.title("APMC Trader System")

    # Database Connection
    connection = create_connection()

    if "login_state" not in st.session_state:
        st.session_state.login_state = None


    if st.session_state.login_state is None:
        # Streamlit Login
        st.sidebar.subheader("Login")
        # Input fields for username and password
        username = st.sidebar.text_input("ID")
        password = st.sidebar.text_input("Password", type="password")
        
        role = st.sidebar.selectbox("Select Role", ["trader", "supplier", "buyer"])

        # Login button
        if st.sidebar.button("Login"):
            user = authenticate_user(username, password, role)
            if user:
                st.success(f"Login Successful! Welcome, {role.capitalize()}!")
                user["role"]=role
                st.session_state.login_state = user
                st.rerun()
            else:
                st.error("Invalid Credentials")
    
    else:
        show_user_menu(connection, st.session_state.login_state)

        if st.sidebar.button("Logout"):
            st.session_state.login_state = None
            st.success("Logout Successful!")
            st.rerun()

# Run the application
if __name__ == "__main__":
    main()
