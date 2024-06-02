import os
import sys
import pandas as pd

# Adjust the path to ensure the 'src','utils' directories can be found
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from process_staged_to_serving import get_feasible_location_data, create_urls_field


def test_get_feasible_location_data():
    # Create a sample DataFrame for testing
    df = pd.DataFrame(
        {
            "location": ["BC", "Vancouver", "Toronto", None],
            "description": [
                "Remote work available",
                "On-site work only",
                "Remote work anywhere",
                "No location specified",
            ],
        }
    )

    # Call the function
    filtered_df = get_feasible_location_data(df)

    # Assert that the filtered DataFrame contains the expected number of rows
    assert (
        len(filtered_df) == 3
    )  # Assuming all rows meet the location or description conditions

    # Assert that the filtered DataFrame contains the correct columns
    assert list(filtered_df.columns) == list(df.columns)


def test_create_urls_field():
    # Create a sample DataFrame for testing
    df = pd.DataFrame(
        {
            "jobProviders": [
                [
                    {"url": "https://www.linkedin.com"},
                    {"url": "https://www.glassdoor.com"},
                    {"url": "https://www.indeed.com"},
                ],
                [
                    {"url": "https://www.example.com"},
                    {"url": "https://www.anotherexample.com"},
                ],
            ]
        }
    )

    # Call the function
    result_df = create_urls_field(df)

    # Assert that the 'urls' column contains the expected values
    expected_urls = [
        "https://www.linkedin.com\n\nhttps://www.glassdoor.com\n\nhttps://www.indeed.com",
        "https://www.example.com\n\nhttps://www.anotherexample.com",
    ]

    # Check if the 'urls' column in the result DataFrame matches the expected values
    assert result_df["urls"].equals(pd.Series(expected_urls))
