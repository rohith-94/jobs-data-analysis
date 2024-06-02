import pandas as pd
import mysql.connector
import logging
from connections import get_mysql_conn
from utils.config import process_config

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def load_parquet_to_mysql(conf, conn):
    """
    Load data from a Parquet file into a MySQL database table.

    Parameters
    ----------
    conf : object
        Configuration object containing paths information.
    conn : mysql.connector.connection_cext.CMySQLConnection
        MySQL connection object.

    Returns
    -------
    None
    """
    parquet_path = conf.paths.serving.parquet_path
    logging.info(f"Reading from {parquet_path}")
    df = pd.read_parquet(parquet_path)

    # Convert all columns to strings
    for column in df.columns:
        df[column] = df[column].astype(str)

    # Create cursor and table
    cursor = conn.cursor()
    db_name = "serving"
    tbl_name = "jobs"

    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {tbl_name} (
        id VARCHAR(255) PRIMARY KEY,
        title TEXT,
        company TEXT,
        skills_llm_gen TEXT,
        sector_llm_gen TEXT,
        location TEXT,
        employmentType TEXT,
        salaryRange TEXT,
        urls TEXT,
        datePosted TEXT,
        date_captured TEXT
    );
    """
    cursor.execute(create_table_query)
    conn.commit()

    logging.info(
        f"Using Database {db_name} - Table {tbl_name} created if previously not present"
    )

    # Prepare the insertion query
    insert_query = """
    INSERT INTO jobs (id, title, company, skills_llm_gen, sector_llm_gen, location, employmentType, salaryRange, urls, datePosted, date_captured)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        title = VALUES(title),
        company = VALUES(company),
        skills_llm_gen = VALUES(skills_llm_gen),
        sector_llm_gen = VALUES(sector_llm_gen),
        location = VALUES(location),
        employmentType = VALUES(employmentType),
        salaryRange = VALUES(salaryRange),
        urls = VALUES(urls),
        datePosted = VALUES(datePosted),
        date_captured = VALUES(date_captured);
    """
    # Convert DataFrame to list of tuples
    data_records = [tuple(row) for row in df.itertuples(index=False, name=None)]

    # Try inserting data
    try:
        cursor.executemany(insert_query, data_records)
        conn.commit()
    except mysql.connector.Error as e:
        logging.error(f"An error occurred: {e}")
        conn.rollback()

    # Clean up
    cursor.close()


if __name__ == "__main__":
    conf = process_config()
    mysql_conn = get_mysql_conn(conf)
    load_parquet_to_mysql(conf, mysql_conn)
    logging.info("Data load to MySQL completed successfully.")
