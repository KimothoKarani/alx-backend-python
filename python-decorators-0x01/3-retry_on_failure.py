import os
import time

import mysql.connector


#create a decorator that retries database operations if they fail due to transient errors

def with_db_connection(func):
    def wrapper(*args, **kwargs):
        password = os.getenv("MYSQL_PASSWORD")

        if not password:
            raise RuntimeError("MYSQL password not set")

        connection = mysql.connector.connect(
            host="localhost",
            user = 'alx_user',
            password = password,
            database = 'ALX_prodev',)

        try:
            return func(connection, *args, **kwargs)
        except mysql.connector.Error as err:
            print(f"OperationalError: {err}")
        finally:
            print("Connection closed")
            connection.close()

    return wrapper


def retry_on_failure(retries=3, delay=1):
    def decorator(func):
        def wrapper(conn, *args, **kwargs):
            last_exception = None
            for attempt in range(1, retries + 1):
                print(f"Attempt {attempt}/{retries}")
                try:
                    result = func(conn, *args, **kwargs)
                    conn.commit()
                    print("Transaction committed successfully")
                    return result
                except Exception as e:
                    last_exception = e
                    print(f"Exception occurred: {e}")
                    conn.rollback()
                    if attempt < retries:
                        print(f"Retrying after {delay} seconds...")
                        time.sleep(delay)
            print("All retry attempts failed.")
            # Optionally, raise last exception or return None
            raise last_exception

        return wrapper
    return decorator

@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM User")
    return cursor.fetchall()

#attempt to fetch users with automatic retry on failure

users = fetch_users_with_retry()
print(users)

