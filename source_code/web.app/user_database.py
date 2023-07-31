import psycopg2
from datetime import datetime


def create_users_table():
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="1234"
    )
    cur = conn.cursor()

    # Create the users table if it doesn't exist
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(100) NOT NULL,
            last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()

    # Insert some initial users into the users table
    cur.execute("""
        INSERT INTO users (username, password)
        VALUES (%s, %s)
    """, ('admin', 'admin123'))

    cur.execute("""
        INSERT INTO users (username, password)
        VALUES (%s, %s)
    """, ('user', 'user123'))

    conn.commit()

    print("Users table created and initial data inserted.")
    conn.close()


if __name__ == "__main__":
    create_users_table()
