import os
import mysql.connector
import uuid
from faker import Faker
from datetime import datetime, timedelta
import random

fake = Faker()

def connect_db():
    password = os.getenv("MYSQL_PASSWORD")
    if not password:
        raise RuntimeError("Please set the MYSQL_PASSWORD environment variable")
    return mysql.connector.connect(
        host="localhost",
        user="alx_user",
        password=password,
        database="ALX_prodev"
    )

def create_tables(conn):
    cursor = conn.cursor()
    tables_sql = [
        """
        CREATE TABLE IF NOT EXISTS User (
            user_id VARCHAR(36) PRIMARY KEY,
            first_name VARCHAR(255) NOT NULL,
            last_name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            phone_number VARCHAR(20),
            role ENUM('guest', 'host', 'admin') NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX (email)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS Property (
            property_id VARCHAR(36) PRIMARY KEY,
            host_id VARCHAR(36) NOT NULL,
            name VARCHAR(255) NOT NULL,
            description TEXT NOT NULL,
            location VARCHAR(255) NOT NULL,
            pricepernight DECIMAL(10,2) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX (host_id),
            FOREIGN KEY (host_id) REFERENCES User(user_id) ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS Booking (
            booking_id VARCHAR(36) PRIMARY KEY,
            property_id VARCHAR(36) NOT NULL,
            user_id VARCHAR(36) NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            total_price DECIMAL(10,2) NOT NULL,
            status ENUM('pending', 'confirmed', 'canceled') NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX (property_id),
            INDEX (user_id),
            FOREIGN KEY (property_id) REFERENCES Property(property_id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS Payment (
            payment_id VARCHAR(36) PRIMARY KEY,
            booking_id VARCHAR(36) NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            payment_method ENUM('credit_card', 'paypal', 'stripe') NOT NULL,
            INDEX (booking_id),
            FOREIGN KEY (booking_id) REFERENCES Booking(booking_id) ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS Review (
            review_id VARCHAR(36) PRIMARY KEY,
            property_id VARCHAR(36) NOT NULL,
            user_id VARCHAR(36) NOT NULL,
            rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
            comment TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (property_id) REFERENCES Property(property_id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS Message (
            message_id VARCHAR(36) PRIMARY KEY,
            sender_id VARCHAR(36) NOT NULL,
            recipient_id VARCHAR(36) NOT NULL,
            message_body TEXT NOT NULL,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sender_id) REFERENCES User(user_id) ON DELETE CASCADE,
            FOREIGN KEY (recipient_id) REFERENCES User(user_id) ON DELETE CASCADE
        )
        """
    ]

    for sql in tables_sql:
        cursor.execute(sql)
    cursor.close()
    conn.commit()
    print("All tables created (if not existed).")

def insert_users(conn, count=100):
    cursor = conn.cursor()
    users = []
    roles = ['guest', 'host', 'admin']
    for _ in range(count):
        user_id = str(uuid.uuid4())
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = fake.unique.email()
        password_hash = fake.sha256()  # dummy hashed password
        phone = fake.phone_number() if random.random() < 0.7 else None
        role = random.choices(roles, weights=[0.7, 0.25, 0.05])[0]
        users.append((user_id, first_name, last_name, email, password_hash, phone, role))
    insert_query = """
        INSERT INTO User 
        (user_id, first_name, last_name, email, password_hash, phone_number, role) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    cursor.executemany(insert_query, users)
    conn.commit()
    cursor.close()
    print(f"Inserted {count} users.")
    return users  # Return list for referencing in other tables

def insert_properties(conn, users, count=50):
    cursor = conn.cursor()
    properties = []
    hosts = [u for u in users if u[6] in ('host', 'admin')]  # filter hosts/admin only
    for _ in range(count):
        property_id = str(uuid.uuid4())
        host = random.choice(hosts)
        host_id = host[0]
        name = fake.company()
        description = fake.text(max_nb_chars=200)
        location = fake.city()
        price = round(random.uniform(30, 500), 2)
        properties.append((property_id, host_id, name, description, location, price))
    insert_query = """
        INSERT INTO Property 
        (property_id, host_id, name, description, location, pricepernight)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.executemany(insert_query, properties)
    conn.commit()
    cursor.close()
    print(f"Inserted {count} properties.")
    return properties

def insert_bookings(conn, users, properties, count=200):
    cursor = conn.cursor()
    bookings = []
    statuses = ['pending', 'confirmed', 'canceled']
    for _ in range(count):
        booking_id = str(uuid.uuid4())
        property_ = random.choice(properties)
        user = random.choice(users)
        start_date = fake.date_between(start_date='-1y', end_date='today')
        end_date = start_date + timedelta(days=random.randint(1, 14))
        total_price = round((end_date - start_date).days * property_[5], 2)
        status = random.choice(statuses)
        bookings.append((booking_id, property_[0], user[0], start_date, end_date, total_price, status))
    insert_query = """
        INSERT INTO Booking
        (booking_id, property_id, user_id, start_date, end_date, total_price, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    cursor.executemany(insert_query, bookings)
    conn.commit()
    cursor.close()
    print(f"Inserted {count} bookings.")
    return bookings

def insert_payments(conn, bookings):
    cursor = conn.cursor()
    payment_methods = ['credit_card', 'paypal', 'stripe']
    payments = []
    for booking in bookings:
        payment_id = str(uuid.uuid4())
        booking_id = booking[0]
        amount = booking[5]
        payment_date = fake.date_time_between(start_date='-1y', end_date='now')
        method = random.choice(payment_methods)
        payments.append((payment_id, booking_id, amount, payment_date, method))
    insert_query = """
        INSERT INTO Payment
        (payment_id, booking_id, amount, payment_date, payment_method)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.executemany(insert_query, payments)
    conn.commit()
    cursor.close()
    print(f"Inserted {len(payments)} payments.")

def insert_reviews(conn, users, properties, count=300):
    cursor = conn.cursor()
    reviews = []
    for _ in range(count):
        review_id = str(uuid.uuid4())
        property_ = random.choice(properties)
        user = random.choice(users)
        rating = random.randint(1, 5)
        comment = fake.paragraph(nb_sentences=3)
        reviews.append((review_id, property_[0], user[0], rating, comment))
    insert_query = """
        INSERT INTO Review
        (review_id, property_id, user_id, rating, comment)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.executemany(insert_query, reviews)
    conn.commit()
    cursor.close()
    print(f"Inserted {count} reviews.")

def insert_messages(conn, users, count=300):
    cursor = conn.cursor()
    messages = []
    for _ in range(count):
        message_id = str(uuid.uuid4())
        sender = random.choice(users)
        recipient = random.choice([u for u in users if u[0] != sender[0]])
        message_body = fake.paragraph(nb_sentences=2)
        messages.append((message_id, sender[0], recipient[0], message_body))
    insert_query = """
        INSERT INTO Message
        (message_id, sender_id, recipient_id, message_body)
        VALUES (%s, %s, %s, %s)
    """
    cursor.executemany(insert_query, messages)
    conn.commit()
    cursor.close()
    print(f"Inserted {count} messages.")

def main():
    conn = connect_db()
    create_tables(conn)
    users = insert_users(conn, 150)        # 150 users
    properties = insert_properties(conn, users, 70)  # 70 properties
    bookings = insert_bookings(conn, users, properties, 300)  # 300 bookings
    insert_payments(conn, bookings)
    insert_reviews(conn, users, properties, 400)    # 400 reviews
    insert_messages(conn, users, 350)                # 350 messages
    conn.close()
    print("Database seeded successfully.")

if __name__ == "__main__":
    main()
