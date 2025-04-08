import psycopg2
from datetime import datetime

from src.utils.config import config

# Database connection parameters
HOST = config.postgres_db['host']
PORT = config.postgres_db['port']
DBNAME = "myaichatmate"
USER = config.postgres_db_username
PASSWORD = config.postgres_db_password

def connect_db():
    try:
        conn = psycopg2.connect(
            host=HOST,
            port=PORT,
            dbname=DBNAME,
            user=USER,
            password=PASSWORD
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None
