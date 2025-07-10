#create a decorator that logs database queries executed by any function
import functools
import os
from pprint import pprint

import mysql.connector


def log_queries(func):
    # Use functools.wraps to preserve the original function's metadata
    # (like its name and docstring). This is a crucial best practice.
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # We expect the query to be passed as a keyword argument, e.g., query="..."
        # The 'kwargs' dictionary holds all keyword arguments.
        sql_query = kwargs.get('query')

        # Now, we log it!
        if sql_query:
            print(f"Executing query: {sql_query}")
            #You could also write to a log file here
            with open("query.log", "a") as f:
                f.write(f"{sql_query}\n")
        else:
            # Good practice to handle cases where the query might be missing
            # or passed as a positional argument.
            print("Query not found in keyword arguments.")

        # Finally, run the original function and return its result.
        return func(*args, **kwargs)

    return wrapper

@log_queries
def fetch_all_users(query):
    password = os.getenv("MYSQL_PASSWORD")
    if not password:
        raise RuntimeError("Please set the MYSQL_PASSWORD environment variable")

    conn = mysql.connector.connect(
        host="localhost",
        user="alx_user",
        password=password,
        database="ALX_prodev"
    )
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results


# --- Main Execution Block ---
if __name__ == "__main__":
    print("-" * 20)

    # 2. Fetch users while logging the query
    # When this line is called, our decorator will intercept it,
    # print the query, and then run the function.
    users = fetch_all_users(query="SELECT * FROM User")

    print("-" * 20)
    print("Users fetched:")
    for user in users:
        pprint(user)


