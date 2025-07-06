#!/usr/bin/python3
"""
A script that calculates the average age of users from a database stream
without loading all data into memory.
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


def stream_user_ages():
    """
    A generator that yields user ages one by one from the database.
    """
    connection = connect_to_prodev()
    if not connection:
        return

    # Using dictionary=True to access the 'age' column by name
    cursor = connection.cursor(dictionary=True)

    try:
        # Optimize by selecting only the 'age' column
        cursor.execute("SELECT age FROM user_data;")

        # Loop 1: Iterate over the cursor and yield each age
        for row in cursor:
            yield row['age']

    finally:
        cursor.close()
        connection.close()


def calculate_average_age():
    """
    Calculates the average age from the generator stream.
    """
    total_age = 0
    user_count = 0

    # Loop 2: Iterate over the ages yielded by the generator
    for age in stream_user_ages():
        total_age += age
        user_count += 1

    # Calculate the average, handle case with no users
    if user_count > 0:
        average_age = total_age / user_count
        print(f"Average age of users: {average_age:.2f}")
    else:
        print("No users found to calculate an average age.")


if __name__ == "__main__":
    calculate_average_age()