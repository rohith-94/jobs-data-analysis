import os
from dotenv import dotenv_values
import google.generativeai as genai
import time
import pandas as pd
from tqdm import tqdm
import logging
from utils.config import process_config

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def get_feasible_location_data(df):
    """
    Filter the DataFrame for feasible locations based on location and description.

    Parameters
    ----------
    df : pandas.DataFrame
        The input DataFrame containing job listings.

    Returns
    -------
    pandas.DataFrame
        Filtered DataFrame with jobs that match the location or description conditions.
    """
    location_condition = df["location"].str.contains(
        "bc|anywhere|vancouver", case=False, na=False
    )
    description_condition = df["description"].str.contains(
        "remote|anywhere", case=False, na=False
    )
    filtered_df = df[location_condition | description_condition]
    return filtered_df


def create_urls_field(df):
    """
    Create a 'urls' field in the DataFrame by extracting URLs from job providers.

    Parameters
    ----------
    df : pandas.DataFrame
        The input DataFrame containing job listings.

    Returns
    -------
    pandas.DataFrame
        DataFrame with an additional 'urls' column.
    """

    def fetch_urls(row):
        priority_urls = ["linkedin", "glassdoor", "indeed"]
        urls = []
        other_urls = []
        for provider in tqdm(row, desc="creating URLs"):
            url = provider.get("url")
            if url:
                if any(priority_url in url for priority_url in priority_urls):
                    urls.append(url)
                else:
                    other_urls.append(url)
        all_urls = urls + other_urls
        return "\n\n".join(all_urls)

    df_copy = df.copy()
    df_copy["urls"] = df_copy["jobProviders"].apply(fetch_urls)
    return df_copy


def generate_llm_fields(df):
    """
    Generate LLM-based fields for skills and sector from job descriptions and company names.

    Parameters
    ----------
    df : pandas.DataFrame
        The input DataFrame containing job listings.

    Returns
    -------
    pandas.DataFrame
        DataFrame with additional 'skills_llm_gen' and 'sector_llm_gen' columns.
    """
    GOOGLE_API_KEY = dict(dotenv_values(".env"))["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")

    base_prompt_template = """
    Read the job description and the company name, then provide keywords of the top 8 required skills and the sector the company belongs to.
    Format this as a string
    skill1, skill2, skill3, skill4, skill5, skill6, skill7, skill8|||sector

    No explanations, unique keywords, no duplicates. Be brief.
    """

    def generate_llm(description, company):
        if pd.isnull(description) or description == "":
            if pd.isnull(company) or company == "":
                return "skills fetch failed|||unknown"
            else:
                prompt = base_prompt_template.format()
                try:
                    response = model.generate_content(company + "\n" + prompt)
                    return "skills fetch failed|||" + response.text.replace("\n", "")
                except Exception as e:
                    logging.error(f"Error generating LLM content: {e}")
                    return "skills fetch failed|||unknown"
        elif pd.isnull(company) or company == "":
            try:
                response = model.generate_content(
                    description + "\n" + base_prompt_template.format()
                )
                return response.text.replace("\n", "") + "|||unknown"
            except Exception as e:
                logging.error(f"Error generating LLM content: {e}")
                return "skills fetch failed|||unknown"
        else:
            try:
                prompt = base_prompt_template.format()
                response = model.generate_content(
                    company + "\n" + description + "\n" + prompt
                )
                return response.text.replace("\n", "")
            except Exception as e:
                logging.error(f"Error generating LLM content: {e}")
                return "skills fetch failed|||unknown"

    skills_llm_gen_list = []
    sector_list = []

    for description, company in zip(df["description"], df["company"]):
        result = generate_llm(description, company)
        skills, sector = result.split("|||")
        skills_llm_gen_list.append(skills.strip())
        sector_list.append(sector.strip())
        time.sleep(5)

    df["skills_llm_gen"] = skills_llm_gen_list
    df["sector_llm_gen"] = sector_list

    return df


def generate_serving_data(conf):
    """
    Generate serving data by processing the staged data and applying various transformations.

    Parameters
    ----------
    conf : object
        Configuration object containing paths information.

    Returns
    -------
    None
    """
    parquet_path = conf.paths.staged.parquet_path
    df = pd.read_parquet(parquet_path)
    filtered_df = get_feasible_location_data(df)
    urls_df = create_urls_field(filtered_df)
    llm_df = generate_llm_fields(urls_df)

    columns = [
        "id",
        "title",
        "company",
        "skills_llm_gen",
        "sector_llm_gen",
        "location",
        "employmentType",
        "salaryRange",
        "urls",
        "datePosted",
        "date_captured",
    ]

    fin_df = llm_df[columns].sort_values(by="date_captured", ascending=False)
    fin_df.to_parquet(conf.paths.serving.parquet_path, index=False)
    logging.info(f"Serving data saved to Parquet at {conf.paths.serving.parquet_path}")


if __name__ == "__main__":
    conf = process_config()
    generate_serving_data(conf)
