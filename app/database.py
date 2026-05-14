import os
from contextlib import contextmanager
import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

load_dotenv()


def get_connection():
    params = dict(
        dbname=os.getenv("DATABASE_NAME", "housing_compliance_demo"),
        user=os.getenv("DATABASE_USER"),
        host=os.getenv("DATABASE_HOST", "localhost"),
        port=os.getenv("DATABASE_PORT", "5432"),
        cursor_factory=RealDictCursor,
    )
    if os.getenv("AZURE_KEYVAULT_URI"):
        from app.key_vault import get_secret
        params["password"] = get_secret("postgresql-password")
    elif password := os.getenv("DATABASE_PASSWORD"):
        params["password"] = password
    ssl_mode = os.getenv("DATABASE_SSL")
    if ssl_mode:
        params["sslmode"] = ssl_mode
    return psycopg2.connect(**params)


@contextmanager
def db_cursor():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            yield cursor
    finally:
        connection.close()
