import os
import json
import pandas as pd
from tqdm import tqdm
from datetime import datetime, timedelta
import logging
from utils.config import process_config

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def get_latest_dirs(md):
    """
    Get the latest directories within the past four days from the main directory.

    Parameters
    ----------
    md : str
        Path to the main directory.

    Returns
    -------
    list of str
        List of subdirectory names within the past four days.
    """
    current_date = datetime.now()
    four_days_ago = current_date - timedelta(days=4)
    subdirs = []

    for subdir in tqdm(os.listdir(md), desc="Scanning directories"):
        subdir_path = os.path.join(md, subdir)
        if os.path.isdir(subdir_path):
            subdir_date = datetime.strptime(subdir, "%d-%m-%Y")
            if four_days_ago <= subdir_date <= current_date:
                subdirs.append(subdir)
    return subdirs


def write_staged_data(conf):
    """
    Process JSON files from the latest directories and write staged data to CSV and Parquet formats.

    Parameters
    ----------
    conf : object
        Configuration object containing paths information.

    Returns
    -------
    None
    """
    main_directory = conf.paths.raw
    dfs = []

    for subdir in tqdm(get_latest_dirs(main_directory), desc="Processing directories"):
        subdir_path = os.path.join(main_directory, subdir)
        if os.path.isdir(subdir_path):
            date_captured = subdir
            dfs_subdir = []

            for filename in tqdm(
                os.listdir(subdir_path), desc=f"Processing files in {subdir}"
            ):
                if filename.endswith(".json"):
                    filepath = os.path.join(subdir_path, filename)
                    with open(filepath, "r") as file:
                        json_data = json.load(file)
                    dfs_subdir.append(pd.DataFrame(json_data["jobs"]))

            combined_df_subdir = pd.concat(dfs_subdir, ignore_index=True)
            combined_df_subdir["date_captured"] = date_captured
            dfs.append(combined_df_subdir)

    combined_df = pd.concat(dfs, ignore_index=True).drop_duplicates(subset=["id"])

    csv_path = conf.paths.staged.csv_path
    combined_df.to_csv(csv_path, index=False)
    logging.info(f"Staged data saved to CSV at {csv_path}")

    parquet_path = conf.paths.staged.parquet_path
    combined_df.to_parquet(parquet_path, index=False)
    logging.info(f"Staged data saved to Parquet at {parquet_path}")


if __name__ == "__main__":
    conf = process_config()
    write_staged_data(conf)
