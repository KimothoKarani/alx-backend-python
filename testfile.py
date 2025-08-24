import time
import sqlite3
import functools
import inspect

# Import connection decorator and error logger
with_db_connection_module = __import__('1-with_db_connection')
with_db_connection = with_db_connection_module.with_db_connection
error_logger = with_db_connection_module.error_logger

# Global dictionary to cache query results
query_cache = {}


def cache_query(func, counter_dict={}):
    """
    A decorator that caches results of SQL queries to avoid re-executing
    the same SELECT query multiple times. Uses a shared in-memory dictionary.

    Also tracks how many times a function is called and the last query string seen.
    If the query is the same as the last, returns the cached result.

    Logs any exception that occurs during query execution.
    """
    counter_dict[func] = 0
    counter_dict['last_query'] = None

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Inspect function signature and bind arguments
        sig = inspect.signature(func)
        bound = sig.bind_partial(*args, **kwargs)
        bound.apply_defaults()

        counter_dict[func] += 1

        # Get current SQL query from bound arguments
        current_query = None
        for name, value in bound.arguments.items():
            if name == 'query':
                current_query = str(value)

        if current_query is None:
            error_logger.warning("No query argument passed to the decorated function.")
            return func(*args, **kwargs)

        # If it's a new query, evaluate and cache it
        if counter_dict['last_query'] != current_query:
            error_logger.info(f"New query detected: {current_query}")
            counter_dict['last_query'] = current_query
            try:
                if current_query in query_cache:
                    return query_cache[current_query]

                result = func(*args, **kwargs)
                if result:
                    query_cache[current_query] = result
                    return result
            except Exception as e:
                error_logger.error(f"Query execution failed: {e}")
        else:
            # If it's a repeated query, return cached result
            error_logger.info(f"Old query: returning cached result for query: {current_query}")
            return query_cache.get(current_query)

    return wrapper


@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    """
    Executes a SELECT query and fetches all user rows.
    Automatically uses cache if the same query was run before.
    """
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()


if __name__ == "__main__":
    # Run test cases to demonstrate caching
    q1 = "SELECT * FROM users;"
    q2 = "SELECT * FROM users WHERE id = 3;"
    q3 = "SELECT * FROM users WHERE id = 1;"

    print("Executing query 1 (first time)")
    users = fetch_users_with_cache(query=q1)
    print(users)

    print("\nExecuting query 1 (cached)")
    users = fetch_users_with_cache(query=q1)
    print(users)

    print("\nExecuting query 2 (first time)")
    users = fetch_users_with_cache(query=q2)
    print(users)

    print("\nExecuting query 2 (cached)")
    users = fetch_users_with_cache(query=q2)
    print(users)

    print("\nExecuting query 3 (first time)")
    users = fetch_users_with_cache(query=q3)
    print(users)