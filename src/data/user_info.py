from src.data.general import connect_db
import psycopg2
from datetime import datetime

from src.utils.logger import logger


def insert_user(user_id: int, has_subscribed: bool, user_name: str, phone_number: str):
    conn = connect_db()
    if conn is None:
        return
    try:
        cur = conn.cursor()
        query = """
        INSERT INTO users (user_id, has_subscribed, user_name, phone_number, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s);
        """
        cur.execute(query, (user_id, has_subscribed, user_name, phone_number, datetime.now(), datetime.now()))
        conn.commit()
        print(f"User with ID {user_id} inserted successfully.")
    except Exception as e:
        print(f"Error inserting user: {e}")
    finally:
        conn.close()

# Function to update user details
def update_user(user_id: int, has_subscribed: bool=None , user_name: str=None, phone_number: str=None):
    conn = connect_db()
    if conn is None:
        return
    try:
        cur = conn.cursor()
        query = "UPDATE users SET updated_at = %s"
        values = [datetime.now()]

        if has_subscribed is not None:
            query += ", has_subscribed = %s"
            values.append(has_subscribed)
        if user_name:
            query += ", user_name = %s"
            values.append(user_name)
        if phone_number:
            query += ", phone_number = %s"
            values.append(phone_number)

        query += " WHERE user_id = %s"
        values.append(user_id)

        cur.execute(query, tuple(values))
        conn.commit()
        logger.info(f"User with ID {user_id} updated successfully.")
    except Exception as e:
        print(f"Error updating user: {e}")
    finally:
        conn.close()

# Function to delete a user
def delete_user(user_id: int):
    conn = connect_db()
    if conn is None:
        return
    try:
        cur = conn.cursor()
        query = "DELETE FROM users WHERE user_id = %s;"
        cur.execute(query, (user_id,))
        conn.commit()
        print(f"User with ID {user_id} deleted successfully.")
    except Exception as e:
        print(f"Error deleting user: {e}")
    finally:
        conn.close()

# Function to fetch all users
def fetch_all_users():
    conn = connect_db()
    if conn is None:
        return
    try:
        cur = conn.cursor()
        query = "SELECT * FROM users;"
        cur.execute(query)
        users = cur.fetchall()
        for user in users:
            print(user)
    except Exception as e:
        print(f"Error fetching users: {e}")
    finally:
        conn.close()

# Example usage:
if __name__ == "__main__":
    # Insert a new user
    insert_user(1, True, 'John Doe', '123-456-7890')

    # Update an existing user
    update_user(1, user_name='Jane Doe', phone_number='098-765-4321')

    # Fetch all users
    fetch_all_users()

    # Delete a user
    # delete_user(1)