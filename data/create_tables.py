import mysql.connector
from pathlib import Path
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

# Execute SQL queries from a file
def execute_sql_file(connection, file_path):
    cursor = connection.cursor()

    # Read SQL queries from the file
    with open(file_path, "r") as sql_file:
        sql_queries = sql_file.read()

    # Split queries (assuming queries are separated by ";")
    queries = sql_queries.split(";")

    # Execute each query
    for query in queries:
        if query.strip():  # Check if the query is not empty
            cursor.execute(query)

    # Commit the changes
    connection.commit()

    # Close the cursor
    cursor.close()

# Main function
def main():
    # Specify the path to your SQL file
    sql_file_path = "create_tables.sql"

    # Connect to the MySQL database
    connection = create_connection()

    # Execute SQL queries from the file
    execute_sql_file(connection, sql_file_path)

    # Close the database connection
    connection.close()

if __name__ == "__main__":
    main()
