#!/usr/bin/python3
"""
A generator function that streams user data from a MySQL database.
"""
import os
import mysql.connector


def connect_to_prodev():
    """Connects to the ALX_prodev database in MYSQL."""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password=os.getenv("MYSQL_PASSWORD"),
            database='ALX_prodev'
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to ALX_prodev database: {err}")
        return None


def stream_users():
    """
    A generator that connects to the database and yields one user row at a time.
    """
    connection = connect_to_prodev()
    if not connection:
        return

    # Using dictionary=True to fetch rows as dictionaries
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("SELECT user_id, name, email, age FROM user_data;")

        # This single loop iterates over the cursor and yields each row
        for row in cursor:
            yield row

    finally:
        cursor.close()
        connection.close()