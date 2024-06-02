import requests
import os
from dotenv import dotenv_values
import json
from datetime import datetime
import logging
from utils.config import process_config

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def write_json_data(conf, url, querystring, headers):
    """
    Fetch JSON data from a given URL and write it to a file.

    Parameters
    ----------
    conf : object
        Configuration object containing path information.
    url : str
        URL to fetch data from.
    querystring : dict
        Query parameters for the GET request.
    headers : dict
        Headers for the GET request.

    Returns
    -------
    None
    """
    response = requests.get(url, headers=headers, params=querystring)
    if response.status_code == 200:
        data = response.json()
        base_folder_path = conf.paths.raw
        os.makedirs(base_folder_path, exist_ok=True)
        current_date = datetime.now().strftime("%d-%m-%Y")
        subfolder_path = os.path.join(base_folder_path, current_date)
        os.makedirs(subfolder_path, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"job_data_{timestamp}.json"
        file_path = os.path.join(subfolder_path, file_name)
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file)
        logging.info(f"JSON data saved to {file_path}")
    elif response.status_code == 429:
        logging.error(f"Plan upgrade Error: {response.json()}")
    else:
        logging.error(f"Error: {response.status_code}")
        logging.error(response.json())


def get_query_strings(conf):
    """
    Generate query strings for the API requests based on the configuration.

    Parameters
    ----------
    conf : object
        Configuration object containing job parameters.

    Returns
    -------
    list of dict
        List of query strings.
    """
    queries = conf.job_params.queries
    location = conf.job_params.location
    language = conf.job_params.language
    remoteOnly = conf.job_params.remoteOnly
    datePosted = conf.job_params.datePosted
    employmentTypes = conf.job_params.employmentTypes
    indices = conf.job_params.indices
    querystrings = []
    for query in queries:
        for index in indices:
            qs = {
                "query": query,
                "location": location,
                "language": language,
                "remoteOnly": remoteOnly,
                "datePosted": datePosted,
                "employmentTypes": employmentTypes,
                "index": index,
            }
            querystrings.append(qs)
    return querystrings


def generate_jsons(conf):
    """
    Generate JSON files by fetching data from the API for each query string.

    Parameters
    ----------
    conf : object
        Configuration object containing API details and job parameters.

    Returns
    -------
    None
    """
    rapid_api_url = conf.rapid_api.url
    env_vars = dict(dotenv_values(".env"))
    headers = {
        "X-RapidAPI-Key": env_vars["RAPID_API_KEY"],
        "X-RapidAPI-Host": conf.rapid_api.host,
    }
    querystrings = get_query_strings(conf)
    for querystring in querystrings:
        logging.info(f"Fetching data with query: {querystring}")
        write_json_data(conf, rapid_api_url, querystring, headers)


if __name__ == "__main__":
    conf = process_config()
    generate_jsons(conf)
