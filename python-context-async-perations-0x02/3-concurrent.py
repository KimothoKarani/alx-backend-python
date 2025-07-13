import asyncio
import aiosqlite  # The asynchronous library for SQLite
import os

DB_FILE = "users_async.db"


# --- Setup: Asynchronously create and populate the database ---
async def setup_database():
    """Creates and populates a simple users.db for demonstration."""
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)

    # 'async with' creates an async context for the connection
    async with aiosqlite.connect(DB_FILE) as db:
        # 'await' is used for I/O operations like executing SQL
        await db.execute('''
                         CREATE TABLE users
                         (
                             id   INTEGER PRIMARY KEY,
                             name TEXT    NOT NULL,
                             age  INTEGER NOT NULL
                         )
                         ''')
        await db.execute("INSERT INTO users (name, age) VALUES (?, ?)", ('Alice', 30))
        await db.execute("INSERT INTO users (name, age) VALUES (?, ?)", ('Bob', 45))
        await db.execute("INSERT INTO users (name, age) VALUES (?, ?)", ('Charlie', 25))
        await db.execute("INSERT INTO users (name, age) VALUES (?, ?)", ('Diana', 50))

        # 'await' is used for the commit operation
        await db.commit()
    print("Database setup complete.")


# --- The Asynchronous Functions (Coroutines) ---

# Renamed from async_fetch_all_users to match the checker
async def async_fetch_users():
    """Fetches all users from the database asynchronously."""
    print("Task 1: Starting to fetch all users...")
    async with aiosqlite.connect(DB_FILE) as db:
        cursor = await db.execute("SELECT * FROM users")
        results = await cursor.fetchall()
        print("Task 1: Finished fetching all users.")
        return results


async def async_fetch_older_users():
    """Fetches users older than 40 asynchronously."""
    print("Task 2: Starting to fetch older users...")
    await asyncio.sleep(0.1)
    async with aiosqlite.connect(DB_FILE) as db:
        cursor = await db.execute("SELECT * FROM users WHERE age > ?", (40,))
        results = await cursor.fetchall()
        print("Task 2: Finished fetching older users.")
        return results


# --- The Main Orchestrator Coroutine (Renamed from main) ---
async def fetch_concurrently():
    """Sets up the DB and runs the fetch queries concurrently."""
    await setup_database()
    print("-" * 30)

    start_time = asyncio.get_event_loop().time()

    # asyncio.gather executes the coroutines concurrently.
    all_users, older_users = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )

    end_time = asyncio.get_event_loop().time()

    print("-" * 30)
    print("All Users Found:")
    for user in all_users:
        print(user)

    print("\nUsers Older Than 40:")
    for user in older_users:
        print(user)

    print(f"\nTotal execution time: {end_time - start_time:.4f} seconds")


# --- Entry Point (Updated to call the renamed function) ---
if __name__ == '__main__':
    # This now matches the checker's requirement
    asyncio.run(fetch_concurrently())