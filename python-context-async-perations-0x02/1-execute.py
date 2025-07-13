# --- The Reusable Query Context Manager ---
import os

import mysql.connector


class ExecuteQuery:
    """
    A context manager that takes a query and parameters, executes it,
    and returns the results, while managing the DB connection.
    """

    def __init__(self, query, params=()):
        """
        Initializes with the query string and a tuple of parameters.
        """
        self.query = query
        self.params = params
        self.conn = None
        self.credentials = {
            'host': 'localhost',
            'user': 'alx_user',
            'password': os.getenv("MYSQL_PASSWORD"),
            'database': 'ALX_prodev'
        }
        if not self.credentials['password']:
            raise ValueError("MYSQL_PASSWORD environment variable not set.")

    def __enter__(self):
        """
        Connects, executes the query, fetches the results, and returns them.
        This is the core of the "one-shot" operation.
        """
        try:
            self.conn = mysql.connector.connect(**self.credentials)
            cursor = self.conn.cursor()

            print(f"Executing query: '{self.query}' with params: {self.params}")
            cursor.execute(self.query, self.params)
            results = cursor.fetchall()

            cursor.close()
            return results  # Return the final result directly

        except mysql.connector.Error as e:
            print(f"Database query failed: {e}")
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Ensures the database connection is closed, no matter what.
        """
        if self.conn and self.conn.is_connected():
            self.conn.close()
            print("Database connection closed.")

        # Return False to let any exceptions propagate.
        return False

if __name__ == "__main__":

    print("-" * 30)

    # The query and parameters are defined here
    # Using %s is the correct placeholder for mysql.connector
    sql_query = "SELECT * FROM users WHERE age > %s"
    age_param = (25,)  # Parameters must be in a tuple

    print("Using the ExecuteQuery context manager:")

    try:
        # The 'with' statement now directly gives us the 'results'.
        # No need to call another method inside the block.
        with ExecuteQuery(sql_query, age_param) as results:
            print("\nQuery Results (Users older than 25):")
            if results:
                for user in results:
                    print(user)
            else:
                print("No users found matching the criteria.")

    except Exception as e:
        print(f"\nAn operation failed: {e}")