#!/usr/bin/python3
"""
A script to fetch and process user data in batches using generators.
"""
import os
import mysql.connector

def connect_to_prodev():
    """Connects to the ALX_prodev database."""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password=os.getenv("MYSQL_PASSWORD"),
            database='ALX_prodev'
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None

def stream_users_in_batches(batch_size=1000):
    """
    A generator that fetches users from the database in batches.
    Each yielded item is a list (batch) of user dictionaries.
    """
    connection = connect_to_prodev()
    if not connection:
        return

    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_data;")

    try:
        while True:
            # Fetch a specific number of rows
            batch = cursor.fetchmany(batch_size)
            # If the batch is empty, we've exhausted the results
            if not batch:
                break
            # Yield the entire batch
            yield batch
    finally:
        cursor.close()
        connection.close()

def batch_processing(batch_size=1000):
    """
    Processes batches of users to filter those over the age of 25.
    """
    # Get the generator for streaming batches
    user_batches = stream_users_in_batches(batch_size)

    # Loop 1: Iterate over each batch yielded by the generator
    for batch in user_batches:
        # Loop 2: Iterate over each user within the batch
        for user in batch:
            # Process the user data
            if user['age'] > 25:
                print(user)