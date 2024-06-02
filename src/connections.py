import psycopg2
import mysql.connector
import logging
from dotenv import dotenv_values


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def get_postgres_conn(conf):
    """
    Connect to PostgreSQL database.

    Args:
        conf (dict): Configuration dictionary.

    Returns:
        psycopg2.connection: PostgreSQL database connection.
    """
    try:
        logging.info("Connecting to Postgres....")
        conn = psycopg2.connect(
            f"postgresql://{conf.connections.postgres.username}:{dict(dotenv_values('.env'))['POSTGRES_PASSWORD']}@{conf.connections.postgres.host}:{conf.connections.postgres.port}/{conf.connections.postgres.database}?sslmode=require"
        )

        # Execute query to fetch version
        query_sql = "SELECT VERSION()"
        cur = conn.cursor()
        cur.execute(query_sql)
        version = cur.fetchone()[0]

        # Log version information
        logging.info(f"PostgreSQL version: {version}")
        logging.info("Connected to PostgreSQL")
        cur.close()
        return conn

    except psycopg2.Error as e:
        # Exception handling for psycopg2 errors
        logging.error(f"Error connecting to PostgreSQL: {e}")
    except Exception as e:
        # Exception handling for other unexpected errors
        logging.error(f"An unexpected error occurred: {e}")


def get_mysql_conn(conf):
    """
    Connect to MySQL database.

    Args:
        conf (dict): Configuration dictionary.

    Returns:
        mysql.connector.connection.MySQLConnection: MySQL database connection.
    """
    try:
        logging.info("Connecting to MySQL....")

        conn = mysql.connector.connect(
            host=conf.connections.mysql.host,
            port=conf.connections.mysql.port,
            user=conf.connections.mysql.username,
            password=dict(dotenv_values(".env"))["MYSQL_PASSWORD"],
            database=conf.connections.mysql.database,
        )

        # Execute query to fetch version
        query_sql = "SELECT VERSION()"
        cursor = conn.cursor()
        cursor.execute(query_sql)
        version = cursor.fetchone()[0]

        # Log version information
        logging.info(f"MySQL version: {version}")
        logging.info("Connected to MySQL")
        return conn

    except mysql.connector.Error as e:
        # Exception handling for MySQL errors
        logging.error(f"Error connecting to MySQL: {e}")
    except Exception as e:
        # Exception handling for other unexpected errors
        logging.error(f"An unexpected error occurred: {e}")
