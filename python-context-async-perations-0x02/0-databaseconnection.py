# --- The Class-Based Context Manager for MySQL ---
import os
import mysql.connector

class DatabaseConnection:
    """
    A context manager to automatically handle MySQL database connections.
    """

    def __init__(self, db_name='ALX_prodev'):
        """
        Initializes the context manager with connection details.
        """
        self.db_name = db_name
        self.connection = None
        self.credentials = {
            'host': 'localhost',
            'user': 'alx_user',  # Using root for simplicity in this example
            'password': os.getenv("MYSQL_PASSWORD"),
            'database': self.db_name
        }
        if not self.credentials['password']:
            raise ValueError("MYSQL_PASSWORD environment variable not set.")

    def __enter__(self):
        """
        The "setup" bookend. Establishes the MySQL connection.
        """
        try:
            self.connection = mysql.connector.connect(**self.credentials)
            print(f"Successfully connected to MySQL database '{self.db_name}'.")
            return self.connection
        except mysql.connector.Error as e:
            print(f"Error connecting to MySQL database: {e}")
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        The "teardown" bookend. Ensures the MySQL connection is closed.
        """
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print(f"MySQL database connection to '{self.db_name}' closed.")

        # Return False to propagate any exceptions that occurred inside the 'with' block.
        return False


# --- Main Execution Block ---
if __name__ == "__main__":

    print("Using the DatabaseConnection context manager for MySQL:")

    try:
        # The 'with' statement creates an instance and calls __enter__
        with DatabaseConnection() as conn:
            # The 'as conn' part receives the connection object returned by __enter__
            cursor = conn.cursor()

            # Perform the query
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()

            print("\nQuery Results:")
            for user in users:
                print(user)

        # __exit__ is automatically called here, closing the connection.
        print("\nExited the 'with' block.")

    except Exception as e:
        print(f"\nAn operation failed: {e}")
