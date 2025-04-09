from dataclasses import dataclass
from typing import Optional

from src.data.connect_db import connect_db
import psycopg2
from datetime import datetime

from src.utils.constants import UserRole
from src.utils.logger import logger

@dataclass
class UserInfo:
    user_id: int
    has_subscribed: bool
    user_name: Optional[str]
    phone_number: Optional[str]
    credits: int
    created_at: datetime
    updated_at: datetime
    role: str
    gender: Optional[str]

def verify_user(user_info: UserInfo) -> bool:
    if user_info is None:
        return False
    if user_info.role == 'admin':
        return True
    if user_info.credits <= 0 or not user_info.has_subscribed:
        return False
    else:
        return True

def get_user(user_id: int) -> Optional[UserInfo]:
    conn = connect_db()
    if conn is None:
        return None
    try:
        cur = conn.cursor()
        query = """
        SELECT user_id, has_subscribed, user_name, phone_number, credits, created_at, updated_at, gender
        FROM users
        WHERE user_id = %s;
        """
        cur.execute(query, (user_id,))
        row = cur.fetchone()
        if row:
            return UserInfo(
                user_id=row[0],
                has_subscribed=row[1],
                user_name=row[2],
                phone_number=row[3],
                created_at=row[4],
                updated_at=row[5],
                gender=row[6],
                credits=row[7],
                role=row[8],
            )
        else:
            logger.info(f"No user found with ID {user_id}")
            return None
    except Exception as e:
        logger.error(f"Error fetching user: {e}")
        return None
    finally:
        conn.close()

def insert_user(user_id: int, has_subscribed: bool, user_name: str, phone_number: str, credits: int, role: str=UserRole.REGULAR.value):
    conn = connect_db()
    if conn is None:
        return
    try:
        cur = conn.cursor()
        query = """
        INSERT INTO users (user_id, has_subscribed, user_name, phone_number, credits, created_at, updated_at, role)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """
        cur.execute(query, (user_id, has_subscribed, user_name, phone_number, credits, datetime.now(), datetime.now(), role))
        conn.commit()
        logger.info(f"User with ID {user_id} inserted successfully.")
    except Exception as e:
        logger.info(f"Error inserting user {user_id}: {e}")
    finally:
        conn.close()

def update_user(user_id: int, has_subscribed: bool=None, user_name: str=None, phone_number: str=None, credits: int=None):
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
        if credits:
            query += ", credits = %s"
            values.append(credits)

        query += " WHERE user_id = %s"
        values.append(user_id)

        cur.execute(query, tuple(values))
        conn.commit()
        logger.info(f"User with ID {user_id} updated successfully.")
    except Exception as e:
        logger.info(f"Error updating user {user_id}: {e}")
    finally:
        conn.close()

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

if __name__ == "__main__":
    # Insert a new user
    insert_user(1, True, 'John Doe', '123-456-7890')

    # Update an existing user
    update_user(1, user_name='Jane Doe', phone_number='098-765-4321')

    # Fetch all users
    fetch_all_users()

    # Delete a user
    # delete_user(1)