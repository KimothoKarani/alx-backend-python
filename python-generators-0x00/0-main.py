#!/usr/bin/python3
"""
Main file to test the seed.py script.
"""

seed = __import__('seed')

# URL for the user data CSV
csv_url = "https://s3.amazonaws.com/alx-intranet.hbtn.io/uploads/misc/2024/12/3888260f107e3701e3cd81af49ef997cf70b6395.csv?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIARDDGGGOUSBVO6H7D%2F20250706%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20250706T082325Z&X-Amz-Expires=86400&X-Amz-SignedHeaders=host&X-Amz-Signature=a04d19421890243e499a32a27ed516a2aa816bda9faddca964c64cc65c9e52eb"

# --- Step 1: Connect to MySQL server and create database ---
connection = seed.connect_db()
if connection:
    seed.create_database(connection)
    connection.close()
    print("Database setup connection closed.")
    print("-" * 20)

# --- Step 2: Connect to the new database and manage tables/data ---
connection = seed.connect_to_prodev()
if connection:
    print("Connection to ALX_prodev successful.")

    # Create the table
    seed.create_table(connection)

    # Insert data from the URL
    seed.insert_data(connection, csv_url)

    # --- Step 3: Verify the results ---
    print("-" * 20)
    print("Verifying data...")
    cursor = connection.cursor()

    # Check if database exists
    cursor.execute("SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = 'ALX_prodev';")
    result = cursor.fetchone()
    if result:
        print("Verification successful: Database 'ALX_prodev' is present.")

    # Check if data was inserted by fetching 5 rows
    cursor.execute("SELECT name, email, age FROM user_data LIMIT 5;")
    rows = cursor.fetchall()
    print("Sample data from user_data table:")
    for row in rows:
        print(row)

    cursor.close()
    connection.close()
    print("-" * 20)
    print("Verification connection closed.")