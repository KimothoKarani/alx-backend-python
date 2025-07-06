#!/usr/bin/python3
"""
A script that uses a generator to lazily paginate through user data.
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


def paginate_users(page_size, offset):
    """Fetches a single 'page' of users from the database."""
    connection = connect_to_prodev()
    if not connection:
        return []

    cursor = connection.cursor(dictionary=True)
    # Using LIMIT and OFFSET for pagination
    cursor.execute(f"SELECT * FROM user_data LIMIT {page_size} OFFSET {offset}")
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return rows


def lazy_paginate(page_size):
    """
    A generator that lazily fetches pages of users one by one.
    """
    offset = 0
    # This single loop continues as long as there is data to fetch
    while True:
        # Fetch the next page of data
        page = paginate_users(page_size=page_size, offset=offset)

        # If the page is empty, there's no more data, so stop.
        if not page:
            break

        # Yield the current page to the caller
        yield page

        # Prepare for the next iteration
        offset += page_size