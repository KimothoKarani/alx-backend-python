import functools
import os
import mysql.connector

#create a decorator that caches the results of a database queries inorder to avoid redundant calls

def with_db_connection(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        password = os.getenv("MYSQL_PASSWORD")

        if not password:
            raise RuntimeError("MYSQL password not set")

        connection = mysql.connector.connect(
            host='localhost',
            port=3306,
            user='alx_user',
            password=password,
            database='ALX_prodev',
        )

        try:
            result = func(connection, *args, **kwargs)
            return result
        except mysql.connector.Error as err:
            print(f"MySQL error: {err}")
        finally:
            print("Closing connection")
            connection.close()

    return wrapper

# --- The Cache and Decorator for Task 4 ---

# 1. The cache MUST be defined in the global scope.
# This ensures it persists between function calls and is shared.
query_cache = {}

def cache_query(func):
    def wrapper(*args, **kwargs):
        cache_key = kwargs.get("query")

        if not cache_key:
            # If no query string is found, we can't cache. Just run the function.
            print("No 'query' argument found, skipping cache.")
            return func(*args, **kwargs)

        # 3. Check if the result is already in our global cache.
        if cache_key in query_cache:
            print(f"CACHE HIT for query: '{cache_key}'")
            return query_cache[cache_key]

        # 4. If not in the cache (a "cache miss"), run the function.
        print(f"CACHE MISS for query: '{cache_key}'. Executing function...")
        result = func(*args, **kwargs)

        # 5. Store the new result in the cache before returning it.
        query_cache[cache_key] = result
        return result
    return wrapper

@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

# First call will cache the result
users = fetch_users_with_cache(query="SELECT * FROM User")

# Second call will use the cached result
users_again = fetch_users_with_cache(query="SELECT * FROM User")


