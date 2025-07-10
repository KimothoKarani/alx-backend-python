import functools
import os
import mysql.connector


#create a decorator that manages database transactions by automatically committing or rolling back changes


def with_db_connection(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        #get the value in **kwargs
        #user_id = kwargs.get('user_id')

        password = os.getenv("MYSQL_PASSWORD")

        if not password:
            raise RuntimeError('MYSQL password is not set')

        connection = mysql.connector.connect(
            host='localhost',
            user='alx_user',
            password=password,
            database='ALX_prodev',
        )

        try:
            # This is where the 'conn' object is "injected" into the next decorator
            return func(connection, *args, **kwargs)
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            # You can also choose to re-raise here if you want:
            # raise
        finally:
            print("Connection closed")
            connection.close()

    return wrapper


def transactional(func):
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        """
         This wrapper receives the 'conn' object from the @with_db_connection decorator.
         """
        try:
            result = func(conn, *args, **kwargs)
            conn.commit()  # commit if successful
            print("Transaction committed successfully")
            return result
        except Exception as e:
            conn.rollback()  # rollback on error
            print(f"Transaction rolled back due to error: {e}")
            raise
    return wrapper

# --- Decorated Function ---
# The order of decorators matters!
# @with_db_connection is on top, so it runs first.
# @transactional is below, so it runs second, receiving 'conn' from the one above.

#First, transactional wraps update_user_email (adds transaction logic).
#Then, with_db_connection wraps that (adds connection management).
@with_db_connection
@transactional
def update_user_email(conn, user_id, new_email):
    cursor = conn.cursor()
    cursor.execute(   "UPDATE User SET email = %s WHERE user_id = %s",
        (new_email, user_id))
    cursor.close()


#### Update user's email with automatic transaction handling

update_user_email(user_id='01593ae1-926a-43c0-ba26-502a257f6ebe', new_email='Crawford_Cartwright@hotmail.com')


