import pandas as pd
import psycopg2
import json
import numpy as np
from connections import get_postgres_conn


# Assuming the connection 'conn' is already set up
def load_parquet_to_postgres(conn):
    parquet_path = "ADD PATH HERE"
    print(f"reading from {parquet_path}")
    df = pd.read_parquet(parquet_path)

    # Convert all columns to strings
    for column in df.columns:
        df[column] = df[column].astype(str)

    # Create cursor and table
    cursor = conn.cursor()
    db_name = "serving"
    tbl_name = "jobs"
    drop_table_query = f"DROP TABLE IF EXISTS {tbl_name};"
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {tbl_name} (
        id TEXT PRIMARY KEY,
        title TEXT,
        company TEXT,
        location TEXT,
        employmentType TEXT,
        datePosted TEXT,
        salaryRange TEXT,
        jobProviders TEXT,
        date_captured TEXT
    );
    """
    cursor.execute(drop_table_query)
    cursor.execute(create_table_query)
    conn.commit()

    print(
        f"Using Database {db_name} - Table {tbl_name} created if previously not present"
    )

    # Prepare the insertion query
    insert_query = """
    INSERT INTO jobs (id, title, company, location, employmentType, datePosted, salaryRange, jobProviders, date_captured)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (id) DO UPDATE SET
        title = EXCLUDED.title,
        company = EXCLUDED.company,
        location = EXCLUDED.location,
        employmentType = EXCLUDED.employmentType,
        datePosted = EXCLUDED.datePosted,
        salaryRange = EXCLUDED.salaryRange,
        jobProviders = EXCLUDED.jobProviders,
        date_captured = EXCLUDED.date_captured;
    """
    # Convert DataFrame to list of tuples
    data_records = [tuple(row) for row in df.itertuples(index=False, name=None)]

    # Try inserting data
    try:
        cursor.executemany(insert_query, data_records)
        conn.commit()
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
        conn.rollback()

    # Clean up
    cursor.close()


if __name__ == "__main__":
    postgres_conn = get_postgres_conn()
    load_parquet_to_postgres(postgres_conn)
