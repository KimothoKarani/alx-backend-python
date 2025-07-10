#create a decorator that automatically handles opening and closing database connections
import functools
import os
from errno import errorcode

import mysql.connector


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

        result = None  # Initialize here to avoid UnboundLocalError
        try:
            result = func(connection, *args, **kwargs)
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            # You can also choose to re-raise here if you want:
            # raise
        finally:
            print("Connection closed")
            connection.close()

        return result


    return wrapper


@with_db_connection
def get_user_by_id(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM User WHERE user_id = %s", (user_id,))
    return cursor.fetchone()


#### Fetch user by ID with automatic connection handling

# import uuid
# test_uuid = uuid.uuid4()
# print(test_uuid)

user = get_user_by_id(user_id=1)
print(user)