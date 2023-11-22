# app/authentication.py
import mysql.connector
from dotenv import load_dotenv
import os

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

# Authenticate user based on username, password, and role in the database
def authenticate_user(username, password, role):
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)

    # Use parameterized query to prevent SQL injection
    query = "SELECT * FROM {} WHERE {}_ID = %s AND password = %s".format(role.lower(), role.lower())
    cursor.execute(query, (username, password))
    user = cursor.fetchone()

    # Close the database connection
    cursor.close()
    connection.close()

    #print("received user, password, role", username, password, role)

    return user
