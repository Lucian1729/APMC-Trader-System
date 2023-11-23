# app/utils.py
import streamlit as st
import mysql.connector
import os
import pandas as pd
from dotenv import load_dotenv
import datetime

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

def fetch_data_procedure(connection, procedure_name, params):
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.callproc(procedure_name, params)
        # Fetch the results after calling the stored procedure
        results = []
        for result in cursor.stored_results():
            results.extend(result.fetchall())
        return results

    finally:
        cursor.close()

# Function to update trader details in the database
def update_trader_details(connection, trader_id, new_name, new_address, new_phone, new_password):
    try:
        # Construct the SQL update query
        update_query = f"""
            UPDATE Trader
            SET name = '{new_name}', 
                address = '{new_address}', 
                phone = '{new_phone}', 
                password = '{new_password}'
            WHERE Trader_ID = {trader_id}
        """

        # Execute the update query
        execute_query(connection, update_query)
                
        return True  # Update successful
    except Exception as e:
        print(f"Error updating trader details: {e}")
        return False  # Update failed

def fetch_supplier_list():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT Supplier_ID, name FROM Supplier")
    supplier_list = cursor.fetchall()
    connection.close()
    return supplier_list

def fetch_buyer_list():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT Buyer_ID, name FROM Buyer")
    buyer_list = cursor.fetchall()
    connection.close()
    return buyer_list

def fetch_transactions_and_balance(transaction_type, entity_id):
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)

    if transaction_type == "With Supplier":
        query = f"""
            SELECT t.Transaction_ID, t.type, t.date, t.quantity, t.total_amount, t.payment_method,
                ts.status AS transaction_status, i.name AS item_name
            FROM Transaction t
            JOIN Transaction_Status ts ON t.Transaction_Status_ID = ts.Transaction_Status_ID
            JOIN Item i ON t.Item_ID = i.Item_ID
            WHERE t.Transaction_ID IN (
                SELECT Transaction_ID FROM Seller_Transaction WHERE Seller_ID = {entity_id}
            )
        """
    elif transaction_type == "With Buyer":
        query = f"""
            SELECT t.Transaction_ID, t.type, t.date, t.quantity, t.total_amount, t.payment_method,
                ts.status AS transaction_status, i.name AS item_name
            FROM Transaction t
            JOIN Transaction_Status ts ON t.Transaction_Status_ID = ts.Transaction_Status_ID
            JOIN Item i ON t.Item_ID = i.Item_ID
            WHERE t.Transaction_ID IN (
                SELECT Transaction_ID FROM Buyer_Transaction WHERE Buyer_ID = {entity_id}
            )
        """

    cursor.execute(query)
    transactions = cursor.fetchall()

    if transaction_type == "With Supplier":
        balance_query = f"SELECT balance_amount FROM Supplier WHERE Supplier_ID = {entity_id}"
    elif transaction_type == "With Buyer":
        balance_query = f"SELECT balance_amount FROM Buyer WHERE Buyer_ID = {entity_id}"

    cursor.execute(balance_query)
    balance_amount = cursor.fetchone()["balance_amount"]

    connection.close()
    return transactions, balance_amount

def fetch_transactions_and_balance_entity(entity_type, entity_id):
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)
    if entity_type == "supplier":
        query = f"""
            SELECT t.*, ts.status AS transaction_status, i.name AS item_name
            FROM Transaction t
            JOIN Transaction_Status ts ON t.Transaction_Status_ID = ts.Transaction_Status_ID
            JOIN Item i ON t.Item_ID = i.Item_ID
            WHERE t.Transaction_ID IN (
                SELECT Transaction_ID FROM Seller_Transaction WHERE Seller_ID = {entity_id}
            )
        """
    elif entity_type == "buyer":
        query = f"""
            SELECT t.*, ts.status AS transaction_status, i.name AS item_name
            FROM Transaction t
            JOIN Transaction_Status ts ON t.Transaction_Status_ID = ts.Transaction_Status_ID
            JOIN Item i ON t.Item_ID = i.Item_ID
            WHERE t.Transaction_ID IN (
                SELECT Transaction_ID FROM Buyer_Transaction WHERE Buyer_ID = {entity_id}
            )
        """

    cursor.execute(query)
    transactions = cursor.fetchall()

    # Fetch balance amount
    balance_query = f"SELECT balance_amount FROM {entity_type.capitalize()} WHERE {entity_type.capitalize()}_ID = {entity_id}"
    balance_amount = fetch_data(connection, balance_query)[0][0]

    return transactions, balance_amount

# Function to fetch Transaction_Status_ID based on status
def fetch_transaction_status_id(status):
    query = f"SELECT Transaction_Status_ID FROM Transaction_Status WHERE status = '{status}'"
    connection = create_connection()
    result = fetch_data(connection, query)
    return result[0][0] if result else None

# Function to fetch the ID of the last inserted row
def fetch_last_inserted_id(connection):
    query = "SELECT LAST_INSERT_ID()"
    result = fetch_data(connection, query)
    return result[0][0] if result else None

def fetch_trader_profile(connection, trader_id):
    query = f"SELECT * FROM Trader WHERE Trader_ID = {trader_id}"
    trader_profile = fetch_data(connection, query)
    return trader_profile[0] if trader_profile else None

def update_item_price(connection, item_id, new_price):
    update_query = f"UPDATE Item SET price_per_unit = {new_price} WHERE Item_ID = {item_id}"
    execute_query(connection, update_query)

def get_menu_options(user_role):
    common_options = ["Home"]
    trader_options = ["Trader Profile", "Employee Management", "Supplier/Buyer Management", "Transactions", "Inventory Management"]
    buyer_options = ["Transaction Recording"]
    supplier_options = ["Transaction Recording"]

    if user_role == "trader":
        return common_options + trader_options
    elif user_role == "buyer":
        return common_options + buyer_options
    elif user_role == "supplier":
        return common_options + supplier_options
    else:
        return common_options

def show_user_menu(connection, user):
    # Streamlit Menu
    menu = get_menu_options(user["role"])
    choice = st.sidebar.selectbox("Menu", menu)

    # Home Page
    if choice == "Home":
        st.subheader(f"Welcome to APMC Trader System, {user['role'].capitalize()}")
        st.write("This is a simple Streamlit+MySQL application for the APMC Trader System.")

    # Trader Profile Page
    elif choice == "Trader Profile":
        st.subheader(f"{user['role'].capitalize()} Profile Management")

        trader_profile = fetch_trader_profile(connection, user["Trader_ID"])

        if trader_profile:
            # Display trader profile details as a table
            profile_info = {
                "Trader_ID": trader_profile[0],
                "Name": trader_profile[1],
                "Address": trader_profile[2],
                "Phone": trader_profile[3],
                "Current Holdings Amount": trader_profile[4],
                "Password": "*" * len(trader_profile[5]),  # Display stars for password
            }

            profile_info_df = pd.DataFrame(profile_info.items(), columns=("Detail", "Value"))
            st.table(profile_info_df)

            # Implement Profile Management UI here
            st.subheader("Edit Trader Details")
            new_name = st.text_input("New Name", trader_profile[1])
            new_address = st.text_input("New Address", trader_profile[2])
            new_phone = st.text_input("New Phone", trader_profile[3])
            new_password = st.text_input("New Password", trader_profile[5], type="password")

            if st.button("Update Details"):
                # Perform update operations in the database
                update_trader_details(connection, user["Trader_ID"], new_name, new_address, new_phone, new_password)

                # Update the user profile with the new details

                updated_profile_info = {
                    "Name": new_name,
                    "Address": new_address,
                    "Phone": new_phone,
                    "Password": "*" * len(new_password),  # Display stars for password
                }
                st.success("Details Updated Successfully!")
            
    # Other Pages based on user role
    elif choice == "Employee Management" and user["role"] == "trader":

        trader_id= user["Trader_ID"]

        st.subheader("Employee Management")
        # Implement Employee Management UI here
        employees_query = f"SELECT * FROM Employee WHERE Trader_ID = {trader_id}"
        employees = fetch_data(connection, employees_query)

        if employees:

            employees= pd.DataFrame(employees, columns=("ID", "Name", "Phone Number", "Salary", "Role", "Employer ID"))
            st.table(employees)
        else:
            st.info("No employees found.")

        total_salary_query = "get_employee_payment"
        total_salary_result = fetch_data_procedure(connection, total_salary_query, (trader_id,))

        if total_salary_result:
            total_salary = total_salary_result[0]["total_payment"]
            st.info(f"Total Monthly Salary for Employees: {total_salary}")

        # Add Employee
        st.subheader("Add Employee")
        new_employee_name = st.text_input("Employee Name")
        new_employee_phone = st.text_input("Employee Phone")
        new_employee_salary = st.number_input("Employee Salary", min_value=0)
        new_employee_role = st.text_input("Employee Role")

        if st.button("Add Employee"):
            # Perform the database insertion for the new employee
            # You need to replace this with your actual SQL insertion query
            insert_employee_query = f"""
                INSERT INTO Employee (name, phone, salary, role, Trader_ID)
                VALUES ('{new_employee_name}', '{new_employee_phone}', {new_employee_salary}, '{new_employee_role}', {trader_id})
            """

            execute_query(connection, insert_employee_query)
            st.success("Employee Added Successfully!")

        # Update Employee Details
        st.subheader("Update Employee Details")
        employee_id_to_update = st.number_input("Employee ID to Update", min_value=1, step=1)

        # Fetch the existing details of the selected employee
        employee_details_query = f"SELECT * FROM Employee WHERE Employee_ID = {employee_id_to_update} AND Trader_ID = {trader_id}"
        employee_details = fetch_data(connection, employee_details_query)

        if employee_details:
            current_employee = employee_details[0]

            # Input fields for updating details
            updated_employee_name = st.text_input("Updated Employee Name", current_employee[1])
            updated_employee_phone = st.text_input("Updated Employee Phone", current_employee[2])
            updated_employee_salary = st.number_input("Updated Employee Salary", value=int(current_employee[3]), min_value=0)
            updated_employee_role = st.text_input("Updated Employee Role", current_employee[4])

            if st.button("Update Employee Details"):
                # Perform the database update for the selected employee
                update_employee_query = f"""
                    UPDATE Employee
                    SET name = '{updated_employee_name}',
                        phone = '{updated_employee_phone}',
                        salary = {updated_employee_salary},
                        role = '{updated_employee_role}'
                    WHERE Employee_ID = {employee_id_to_update} AND Trader_ID = {trader_id}
                """

                execute_query(connection, update_employee_query)
                st.success("Employee Details Updated Successfully!")
        else:
            st.warning("Employee not found.")
        
        # Delete Employee
        st.subheader("Delete Employee")
        employee_id_to_delete = st.number_input("Employee ID to Delete", min_value=1, step=1)
        employee_details_query = f"SELECT * FROM Employee WHERE Employee_ID = {employee_id_to_delete} AND Trader_ID = {trader_id}"
        employee_to_delete_details = fetch_data(connection, employee_details_query)

        # Confirmation checkbox
        confirmation = st.checkbox("Confirm Deletion")

        delete_button_key = f"delete_employee_{employee_id_to_delete}"
        if confirmation and st.button("Delete Employee", key=delete_button_key):
            if employee_to_delete_details:
                # Perform the database deletion for the selected employee
                delete_employee_query = f"DELETE FROM Employee WHERE Employee_ID = {employee_id_to_delete} AND Trader_ID = {trader_id}"
                execute_query(connection, delete_employee_query)
                st.success("Employee Deleted Successfully!")
            else:
                st.warning("Employee not found.")
        elif (not confirmation) and st.button("Delete Employee"):
            st.warning("Please confirm the deletion.")

    elif choice == "Supplier/Buyer Management" and user["role"] == "trader":
        st.subheader("Supplier/Buyer Management")
        
        entity_type = st.radio("Select Entity Type", ["Supplier", "Buyer"])

        if entity_type == "Supplier":
            st.subheader("Supplier Management")

            # Add Supplier
            st.subheader("Add Supplier")
            new_supplier_name = st.text_input("Supplier Name")
            new_supplier_address = st.text_input("Supplier Address")
            new_supplier_phone = st.text_input("Supplier Phone")
            new_supplier_password = st.text_input("Supplier Password", type="password")

            if st.button("Add Supplier"):
                # Perform the database insertion for the new supplier
                # You need to replace this with your actual SQL insertion query
                insert_supplier_query = f"""
                    INSERT INTO Supplier (name, address, phone, balance_amount, password)
                    VALUES ('{new_supplier_name}', '{new_supplier_address}', '{new_supplier_phone}', 0.0, '{new_supplier_password}')
                """

                execute_query(connection, insert_supplier_query)
                st.success("Supplier Added Successfully!")

            # Update Supplier Details
            st.subheader("Update Supplier Details")
            supplier_id_to_update = st.number_input("Supplier ID to Update", min_value=1, step=1)

            # Fetch the existing details of the selected supplier
            supplier_details_query = f"SELECT * FROM Supplier WHERE Supplier_ID = {supplier_id_to_update}"
            supplier_details = fetch_data(connection, supplier_details_query)

            if supplier_details:
                current_supplier = supplier_details[0]

                # Input fields for updating details
                updated_supplier_name = st.text_input("Updated Supplier Name", current_supplier[1])
                updated_supplier_address = st.text_input("Updated Supplier Address", current_supplier[2])
                updated_supplier_phone = st.text_input("Updated Supplier Phone", current_supplier[3])
                updated_supplier_password = st.text_input("Updated Supplier Password", type="password", value=current_supplier[5])

                if st.button("Update Supplier Details"):
                    # Perform the database update for the selected supplier
                    update_supplier_query = f"""
                        UPDATE Supplier
                        SET name = '{updated_supplier_name}',
                            address = '{updated_supplier_address}',
                            phone = '{updated_supplier_phone}',
                            password = '{updated_supplier_password}'
                        WHERE Supplier_ID = {supplier_id_to_update}
                    """

                    execute_query(connection, update_supplier_query)
                    st.success("Supplier Details Updated Successfully!")
            else:
                st.warning("Supplier not found.")
            
            # Delete Supplier
            st.subheader("Delete Supplier")
            supplier_id_to_delete = st.number_input("Supplier ID to Delete", min_value=1, step=1)
            supplier_details_query = f"SELECT * FROM Supplier WHERE Supplier_ID = {supplier_id_to_delete}"
            supplier_to_delete_details = fetch_data(connection, supplier_details_query)

            # Confirmation checkbox
            confirmation = st.checkbox("Confirm Deletion")

            delete_button_key = f"delete_supplier_{supplier_id_to_delete}"
            if confirmation and st.button("Delete Supplier", key=delete_button_key):
                if supplier_to_delete_details:
                    # Perform the database deletion for the selected supplier
                    delete_supplier_query = f"DELETE FROM Supplier WHERE Supplier_ID = {supplier_id_to_delete}"
                    execute_query(connection, delete_supplier_query)
                    st.success("Supplier Deleted Successfully!")
                else:
                    st.warning("Supplier not found.")
            elif (not confirmation) and st.button("Delete Supplier"):
                st.warning("Please confirm the deletion.")

        elif entity_type == "Buyer":
            st.subheader("Buyer Management")

            # Add Buyer
            st.subheader("Add Buyer")
            new_buyer_name = st.text_input("Buyer Name")
            new_buyer_address = st.text_input("Buyer Address")
            new_buyer_phone = st.text_input("Buyer Phone")
            new_buyer_password = st.text_input("Buyer Password", type="password")

            if st.button("Add Buyer"):
                # Perform the database insertion for the new buyer
                # You need to replace this with your actual SQL insertion query
                insert_buyer_query = f"""
                    INSERT INTO Buyer (name, address, phone, balance_amount, password)
                    VALUES ('{new_buyer_name}', '{new_buyer_address}', '{new_buyer_phone}', 0.0, '{new_buyer_password}')
                """

                execute_query(connection, insert_buyer_query)
                st.success("Buyer Added Successfully!")

            # Update Buyer Details
            st.subheader("Update Buyer Details")
            buyer_id_to_update = st.number_input("Buyer ID to Update", min_value=1, step=1)

            # Fetch the existing details of the selected buyer
            buyer_details_query = f"SELECT * FROM Buyer WHERE Buyer_ID = {buyer_id_to_update}"
            buyer_details = fetch_data(connection, buyer_details_query)

            if buyer_details:
                current_buyer = buyer_details[0]

                # Input fields for updating details
                updated_buyer_name = st.text_input("Updated Buyer Name", current_buyer[1])
                updated_buyer_address = st.text_input("Updated Buyer Address", current_buyer[2])
                updated_buyer_phone = st.text_input("Updated Buyer Phone", current_buyer[3])
                updated_buyer_password = st.text_input("Updated Buyer Password", type="password", value=current_buyer[5])

                if st.button("Update Buyer Details"):
                    # Perform the database update for the selected buyer
                    update_buyer_query = f"""
                        UPDATE Buyer
                        SET name = '{updated_buyer_name}',
                            address = '{updated_buyer_address}',
                            phone = '{updated_buyer_phone}',
                            password = '{updated_buyer_password}'
                        WHERE Buyer_ID = {buyer_id_to_update}
                    """

                    execute_query(connection, update_buyer_query)
                    st.success("Buyer Details Updated Successfully!")
            else:
                st.warning("Buyer not found.")
            
            # Delete Buyer
            st.subheader("Delete Buyer")
            buyer_id_to_delete = st.number_input("Buyer ID to Delete", min_value=1, step=1)
            buyer_details_query = f"SELECT * FROM Buyer WHERE Buyer_ID = {buyer_id_to_delete}"
            buyer_to_delete_details = fetch_data(connection, buyer_details_query)

            # Confirmation checkbox
            confirmation = st.checkbox("Confirm Deletion")

            delete_button_key = f"delete_buyer_{buyer_id_to_delete}"
            if confirmation and st.button("Delete Buyer", key=delete_button_key):
                if buyer_to_delete_details:
                    # Perform the database deletion for the selected buyer
                    delete_buyer_query = f"DELETE FROM Buyer WHERE Buyer_ID = {buyer_id_to_delete}"
                    execute_query(connection, delete_buyer_query)
                    st.success("Buyer Deleted Successfully!")
                else:
                    st.warning("Buyer not found.")
            elif (not confirmation) and st.button("Delete Buyer"):
                st.warning("Please confirm the deletion.")


    elif choice == "Transactions" and user["role"] == "trader":
        st.subheader("Transactions")
        
        transaction_type = st.radio("Select Transaction Type", ["With Supplier", "With Buyer"])

        supplier_list = fetch_supplier_list()
        buyer_list = fetch_buyer_list()

        transaction_column_names = ['Transaction_ID', 'type', 'date', 'quantity', 'total_amount', 'payment_method',
                                     'transaction_status', 'item_name']


        if transaction_type == "With Supplier":
            supplier_entity = st.selectbox("Select Supplier", [f"{supplier[1]} (ID: {supplier[0]})" for supplier in supplier_list])
            supplier_id = int(supplier_entity.split("(ID: ")[1].split(")")[0])
            
            # Retrieve and display supplier profile information
            supplier_profile_query = f"SELECT Supplier_ID, name, address, phone FROM Supplier WHERE Supplier_ID = {supplier_id}"
            supplier_profile = fetch_data(connection, supplier_profile_query)
            supplier_profile_df = pd.DataFrame(supplier_profile, columns=["Supplier_ID", "Name", "Address", "Phone"])
            st.write("Supplier Profile:")
            st.table(supplier_profile_df)

            # Retrieve and display transactions and balance amount with the selected supplier
            transactions, balance_amount = fetch_transactions_and_balance("With Supplier", supplier_id)

            # Convert transactions to a pandas DataFrame
            transactions_df = pd.DataFrame(transactions, columns=transaction_column_names)

            # Display transactions as a table
            st.table(transactions_df)

            # Display balance amount
            st.info(f"Balance Amount to be paid to {supplier_entity}: {balance_amount}")

        elif transaction_type == "With Buyer":
            buyer_entity = st.selectbox("Select Buyer", [f"{buyer[1]} (ID: {buyer[0]})" for buyer in buyer_list])
            buyer_id = int(buyer_entity.split("(ID: ")[1].split(")")[0])

            # Retrieve and display buyer profile information
            buyer_profile_query = f"SELECT Buyer_ID, name, address, phone FROM Buyer WHERE Buyer_ID = {buyer_id}"
            buyer_profile = fetch_data(connection, buyer_profile_query)
            buyer_profile_df = pd.DataFrame(buyer_profile, columns=["Buyer_ID", "Name", "Address", "Phone"])
            st.write("Buyer Profile:")
            st.table(buyer_profile_df)

            # Retrieve and display transactions and balance amount with the selected buyer
            transactions, balance_amount = fetch_transactions_and_balance("With Buyer", buyer_id)

            # Convert transactions to a pandas DataFrame
            transactions_df = pd.DataFrame(transactions, columns=transaction_column_names)

            # Display transactions as a table
            st.table(transactions_df)

            # Display balance amount
            st.info(f"Balance Amount to be paid by {buyer_entity}: {balance_amount}")

        # Add Transaction
        st.subheader("Add Transaction")
        transaction_date = st.date_input("Transaction Date", datetime.date.today())
        transaction_quantity = st.number_input("Quantity", min_value=1, step=1)
        transaction_total_amount = st.number_input("Total Amount", min_value=0.0)
        transaction_payment_method = st.text_input("Payment Method")
        item_id = st.number_input("Item ID", min_value=1, step=1)


        if transaction_type == "With Supplier":
            selected_supplier = st.selectbox("Select supplier you are transacting with", [f"{supplier[1]} (ID: {supplier[0]})" for supplier in supplier_list])
            entity_id = int(selected_supplier.split("(ID: ")[1].split(")")[0])
            entity_type = "Seller"
        else:
            selected_buyer = st.selectbox("Select buyer you are transacting with", [f"{buyer[1]} (ID: {buyer[0]})" for buyer in buyer_list])
            entity_id = int(selected_buyer.split("(ID: ")[1].split(")")[0])
            entity_type = "Buyer"
        
        if st.button("Add Transaction"):

            # Perform the database insertion for the new transaction
            # Set the initial status of the transaction to "initialised"
            initial_status = "initialised"
            insert_transaction_query = f"""
                INSERT INTO Transaction (type, date, quantity, total_amount, payment_method, Trader_ID, Transaction_Status_ID, Item_ID)
                VALUES ('{transaction_type}', '{transaction_date}', {transaction_quantity}, {transaction_total_amount}, 
                        '{transaction_payment_method}', {user["Trader_ID"]}, {fetch_transaction_status_id(initial_status)}, {item_id})
            """
            execute_query(connection, insert_transaction_query)

            # Retrieve the ID of the newly added transaction
            transaction_id = fetch_last_inserted_id(connection)

            # Insert into Seller_Transaction or Buyer_Transaction based on the transaction type
            if transaction_type == "With Supplier":
                seller_id = entity_id
                insert_seller_transaction_query = f"""
                    INSERT INTO Seller_Transaction (Transaction_ID, Seller_ID)
                    VALUES ({transaction_id}, {seller_id})
                """
                execute_query(connection, insert_seller_transaction_query)
            elif transaction_type == "With Buyer":
                buyer_id = entity_id
                insert_buyer_transaction_query = f"""
                    INSERT INTO Buyer_Transaction (Transaction_ID, Buyer_ID)
                    VALUES ({transaction_id}, {buyer_id})
                """
                execute_query(connection, insert_buyer_transaction_query)

            # Display success message
            st.success("Transaction Added Successfully!")


        # Modify Transaction Status
        st.subheader("Modify Transaction Status")

        # Allow the user to select a transaction by Transaction ID
        selected_transaction_id = st.number_input("Select Transaction ID", min_value=1, step=1)

        # Fetch the current status of the selected transaction
        current_status_query = f"SELECT Transaction_Status_ID FROM Transaction WHERE Transaction_ID = {selected_transaction_id}"
        current_status_id = fetch_data(connection, current_status_query)

        if current_status_id:
            current_status_id = current_status_id[0][0]

            # Fetch the corresponding status string
            current_status_string_query = f"SELECT status FROM Transaction_Status WHERE Transaction_Status_ID = {current_status_id}"
            current_status_string = fetch_data(connection, current_status_string_query)[0][0]

            st.info(f"Current Status of Transaction {selected_transaction_id}: {current_status_string}")

            # Define the possible status modifications based on the current status
            if current_status_string == "initialised":
                new_status_options = ["cancelled", "fulfilled", "completed"]
            elif current_status_string == "fulfilled":
                new_status_options = ["completed"]
            else:
                new_status_options = []

            if new_status_options:
                new_status = st.selectbox("Select New Transaction Status", new_status_options)

                if st.button("Modify Transaction Status"):
                    # Perform the database update for the new transaction status
                    update_transaction_status_query = f"""
                        UPDATE Transaction
                        SET Transaction_Status_ID = {fetch_transaction_status_id(new_status)}
                        WHERE Transaction_ID = {selected_transaction_id};
                    """
                    execute_query(connection, update_transaction_status_query)

                    st.success(f"Transaction {selected_transaction_id} status modified to {new_status} successfully!")
            else:
                st.warning("Cannot modify the transaction status based on the current status.")
        else:
            st.warning("Invalid Transaction ID. Please enter a valid Transaction ID.")

    elif choice == "Inventory Management" and user["role"] == "trader":
        st.subheader("Inventory Management")
        # Implement Inventory Management UI here
        items = fetch_data(connection, "SELECT * FROM Item")
        if items:
            st.write("All Items:")
            items_df = pd.DataFrame(items, columns=["Item_ID", "Name", "Type", "Grade", "Price_per_Unit", "Current_Stock"])
            st.table(items_df)
        else:
            st.warning("No items found.")

        # Add a new item
        st.subheader("Add a New Item")
        new_item_name = st.text_input("Item Name")
        new_item_type = st.text_input("Item Type")
        new_item_grade = st.text_input("Item Grade")
        new_item_price = st.number_input("Price per Unit", min_value=0.0)

        if st.button("Add Item"):
            add_item_query = f"""
                INSERT INTO Item (name, type, grade, price_per_unit, current_stock)
                VALUES ('{new_item_name}', '{new_item_type}', '{new_item_grade}', {new_item_price}, 0)
            """
            execute_query(connection, add_item_query)
            st.success("Item Added Successfully!")
        
        st.subheader("Update Item Price")
        item_id_to_update = st.number_input("Item ID to Update", min_value=1, step=1)

        # Fetch the existing details of the selected item
        item_details_query = f"SELECT * FROM Item WHERE Item_ID = {item_id_to_update}"
        item_details = fetch_data(connection, item_details_query)

        if item_details:
            current_item = item_details[0]

            # Input field for updating price
            updated_item_price = st.number_input("Updated Price per Unit", value=float(current_item[4]), min_value=0.0)

            if st.button("Update Item Price"):
                # Perform the database update for the selected item
                update_item_price(connection, item_id_to_update, updated_item_price)
                st.success("Item Price Updated Successfully!")
        else:
            st.warning("Item not found.")

    elif choice == "Transaction Recording" and user["role"] in ["supplier", "buyer"]:
        st.subheader("Transaction Recording")

        entity_type = user["role"]
        entity_id = user[f"{entity_type.capitalize()}_ID"]

        # Fetch and display transactions and balance amount
        transactions, balance_amount = fetch_transactions_and_balance_entity(entity_type, entity_id)

        # Convert transactions to a pandas DataFrame
        transaction_column_names = ['Transaction_ID', 'type', 'date', 'quantity', 'total_amount', 'payment_method',
                                     'transaction_status', 'item_name']
        if transactions:
            transactions_df = pd.DataFrame(transactions, columns=transaction_column_names)

            # Display transactions as a table
            st.write(f"All Transactions for {entity_type.capitalize()}:")
            st.table(transactions_df)

        # Display balance amount
        st.info(f"Balance Amount: {balance_amount}")