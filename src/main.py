import logging
from connections import get_mysql_conn
from fetch_json_response import generate_jsons
from process_json_to_staged import write_staged_data
from process_staged_to_serving import generate_serving_data
from process_serving_to_mysql import load_parquet_to_mysql
from utils.config import process_config

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def main():
    """
    Main function to orchestrate the ETL process.

    Steps include:
    - Processing configuration
    - Establishing MySQL connection
    - Generating JSONs from an API
    - Writing staged data
    - Generating serving data
    - Loading data into MySQL

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    conf = process_config()
    mysql_conn = get_mysql_conn(conf)
    # generate_jsons(conf)
    logging.info("Writing staged data...")
    write_staged_data(conf)
    logging.info("Generating serving data...")
    generate_serving_data(conf)
    logging.info("Loading data into MySQL...")
    load_parquet_to_mysql(conf, mysql_conn)
    logging.info("ETL process completed successfully.")


if __name__ == "__main__":
    main()
