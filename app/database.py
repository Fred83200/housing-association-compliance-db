import os
from contextlib import contextmanager
import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

load_dotenv()


def get_connection():
    return psycopg2.connect(
        dbname=os.getenv("DATABASE_NAME", "housing_compliance_demo"),
        user=os.getenv("DATABASE_USER", "amy.breslin"),
        host=os.getenv("DATABASE_HOST", "localhost"),
        port=os.getenv("DATABASE_PORT", "5432"),
        cursor_factory=RealDictCursor,
    )


@contextmanager
def db_cursor():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            yield cursor
    finally:
        connection.close()