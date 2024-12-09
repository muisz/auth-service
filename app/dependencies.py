import psycopg2
import os

def get_database_connection():
    connection = psycopg2.connect(
        database=os.environ.get('DB_NAME'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        host=os.environ.get('DB_HOST'),
        port=os.environ.get('DB_PORT'),
    )
    try:
        yield connection
    finally:
        connection.close()
