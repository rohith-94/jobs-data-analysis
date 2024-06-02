import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
from dotenv import dotenv_values
from utils.config import process_config

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def dataframe_to_html(df):
    """
    Convert DataFrame to HTML table.

    Parameters
    ----------
    df : pandas.DataFrame
        The input DataFrame.

    Returns
    -------
    str
        HTML representation of the DataFrame.
    """
    return df.to_html(index=False, escape=False)


def send_email(subject, html_content, sender_email, sender_password, receiver_email):
    """
    Send an email with HTML content.

    Parameters
    ----------
    subject : str
        The subject of the email.
    html_content : str
        The HTML content of the email.
    sender_email : str
        The sender's email address.
    sender_password : str
        The sender's email password.
    receiver_email : str
        The receiver's email address.

    Returns
    -------
    None
    """
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(html_content, "html"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        logging.info("Email sent successfully!")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        server.quit()


def convert_date_column(df):
    """
    Convert the date_captured column to datetime type.

    Parameters
    ----------
    df : pandas.DataFrame
        The input DataFrame.

    Returns
    -------
    pandas.DataFrame
        DataFrame with date_captured column as datetime.
    """
    df["date_captured"] = pd.to_datetime(df["date_captured"], format="%d-%m-%Y")
    return df


def count_jobs(df):
    """
    Count the number of jobs refreshed or updated and the total number of jobs for that day.

    Parameters
    ----------
    df : pandas.DataFrame
        The input DataFrame.

    Returns
    -------
    int
        The number of jobs refreshed or updated.
    """
    max_date = df["date_captured"].max()
    max_date_df = df[df["date_captured"] == max_date]
    refreshed_jobs_count = len(max_date_df)
    return refreshed_jobs_count


def identify_top_locations(df):
    """
    Identify the top locations based on frequency.

    Parameters
    ----------
    df : pandas.DataFrame
        The input DataFrame.

    Returns
    -------
    pandas.Series
        Series with top locations and their frequencies.
    """
    max_date_df = df[df["date_captured"] == df["date_captured"].max()]
    top_locations = max_date_df["location"].value_counts().head(5)
    return top_locations


def identify_top_sectors(df):
    """
    Identify the top sectors where jobs are posted.

    Parameters
    ----------
    df : pandas.DataFrame
        The input DataFrame.

    Returns
    -------
    pandas.Series
        Series with top sectors and their frequencies.
    """
    top_sectors = df["sector_llm_gen"].value_counts().head(5)
    return top_sectors


def check_education_jobs_presence(df):
    """
    Determine if jobs from the education sector are present.

    Parameters
    ----------
    df : pandas.DataFrame
        The input DataFrame.

    Returns
    -------
    bool
        True if education jobs are present, False otherwise.
    """
    education_jobs_present = any(
        "edu" in sector.lower() for sector in df["sector_llm_gen"]
    )
    return education_jobs_present


def filter_education_jobs(df):
    """
    Filter rows where the sector contains 'edu' (case insensitive).

    Parameters
    ----------
    df : pandas.DataFrame
        The input DataFrame.

    Returns
    -------
    pandas.DataFrame
        DataFrame with education sector jobs.
    """
    education_jobs = df[df["sector_llm_gen"].str.contains("edu", case=False)].copy()
    return education_jobs


def replace_newline_with_space(df):
    """
    Replace '\n' with space in the 'urls' column.

    Parameters
    ----------
    df : pandas.DataFrame
        The input DataFrame.

    Returns
    -------
    pandas.DataFrame
        DataFrame with URLs column updated.
    """
    df["urls"] = df["urls"].str.replace("\n", " ")
    return df


def convert_to_html(df):
    """
    Convert DataFrame to HTML.

    Parameters
    ----------
    df : pandas.DataFrame
        The input DataFrame.

    Returns
    -------
    str
        HTML representation of the DataFrame.
    """
    return df.to_html(index=False, justify="left")


def get_css():
    """
    Get the CSS styling for tables.

    Returns
    -------
    str
        CSS styling as a string.
    """
    return """<style>
    table.my-table {
        border-collapse: collapse;
        width: 100%;
    }
    th, td {
        padding: 8px;
        text-align: left;
        border-bottom: 0.25px solid #ddd;
        border-right: 0.25px solid #ddd;
    }
    th {
        background-color: #f2f2f2;
        border-right: none;
    }
    </style>"""


def deliver_data(conf):
    """
    Deliver data by generating HTML content from a DataFrame and sending it via email.

    Parameters
    ----------
    conf : object
        Configuration object containing paths and email information.

    Returns
    -------
    None
    """
    logging.info("Loading data from parquet file.")
    df = pd.read_parquet(conf.paths.serving.parquet_path)

    logging.info("Converting date column.")
    df = convert_date_column(df)

    logging.info("Counting jobs.")
    jobs_count = count_jobs(df)

    logging.info("Identifying top locations.")
    top_locations = identify_top_locations(df)

    logging.info("Identifying top sectors.")
    top_sectors = identify_top_sectors(df)

    logging.info("Checking education jobs presence.")
    education_jobs_present = check_education_jobs_presence(df)

    logging.info("Filtering education jobs.")
    education_jobs = filter_education_jobs(df)

    logging.info("Replacing newlines with spaces in URLs.")
    education_jobs = replace_newline_with_space(education_jobs)

    logging.info("Converting dataframes to HTML.")
    top_locations_html = convert_to_html(top_locations.reset_index())
    top_sectors_html = convert_to_html(top_sectors.reset_index())
    education_html = convert_to_html(
        education_jobs[["company", "location", "sector_llm_gen", "urls"]]
    )

    max_date = df["date_captured"].max()
    html_content = f"<p>Total number of jobs (new/refreshed) for {max_date.strftime('%Y-%m-%d')} : {jobs_count}</p>"
    html_content += f"<p>Top locations:</p>{top_locations_html}"
    html_content += f"<p>Top sectors:</p>{top_sectors_html}"
    html_content += f"<p>Jobs from education sector generated: <b>{'YES' if education_jobs_present else 'NO'}</b></p>"
    html_content += f"<h2>Education Sector Jobs</h2>{education_html}"
    css_html_content = get_css() + html_content

    logging.info("Sending email.")
    send_email(
        conf.email.subject,
        css_html_content,
        conf.email.sender_email,
        dict(dotenv_values(".env"))["GOOGLE_MAIL_DELIVER_PASS"],
        conf.email.receiver_email,
    )


if __name__ == "__main__":
    conf = process_config()
    deliver_data(conf)
    logging.info("Data delivery completed.")
