import os
import mysql.connector
import csv
import uuid
import pandas as pd

def connect_db():
    """
    Connect to MySQL server (no database specified yet).
    Password is pulled from the MYSQL_PASSWORD environment variable.
    """
    password = os.getenv("MYSQL_PASSWORD")
    if not password:
        raise RuntimeError("Please set the MYSQL_PASSWORD environment variable")
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password=password
    )

def create_database(connection):
    """
    Create ALX_prodev if it doesn’t exist.
    """
    cursor = connection.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev;")
    cursor.close()
    connection.commit()

def connect_to_prodev():
    """
    Connect specifically to ALX_prodev.
    Password is pulled from the MYSQL_PASSWORD environment variable.
    """
    password = os.getenv("MYSQL_PASSWORD")
    if not password:
        raise RuntimeError("Please set the MYSQL_PASSWORD environment variable")
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password=password,
        database="ALX_prodev"
    )

def create_table(connection):
    """Creates a table user_data if it does not exist with the required fields."""
    cursor = connection.cursor()
    table_description = """
    CREATE TABLE IF NOT EXISTS user_data (
        user_id VARCHAR(36) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        age DECIMAL NOT NULL
    )
    """
    try:
        cursor.execute(table_description)
        print("Table 'user_data' created successfully or already exists.")
    except mysql.connector.Error as err:
        print(f"Failed to create table: {err}")
    finally:
        cursor.close()


def insert_data(connection, file_path):
    """
    Reads data from a CSV, generates a UUID for each row,
    and inserts it into the database.
    """
    cursor = connection.cursor()
    try:
        # The URL you provided is a direct download link.
        # Pandas can read directly from a URL.
        df = pd.read_csv(file_path)

        insert_query = """
                       INSERT INTO user_data (user_id, name, email, age)
                       VALUES (%s, %s, %s, %s) \
                       """

        for index, row in df.iterrows():
            # Generate a new UUID for each user
            user_id = str(uuid.uuid4())

            # Create the tuple of data to insert
            data_tuple = (user_id, row['name'], row['email'], row['age'])
            cursor.execute(insert_query, data_tuple)

        connection.commit()
        print(f"Data from {file_path} inserted successfully.")
    except Exception as err:
        print(f"Error inserting data: {err}")
        connection.rollback()
    finally:
        cursor.close()

def stream_user_data(connection):
    """
    A generator that yields one row at a time from user_data.
    """
    cursor = connection.cursor()
    cursor.execute("SELECT user_id, name, email, age FROM user_data;")
    for record in cursor:
        yield record
    cursor.close()




