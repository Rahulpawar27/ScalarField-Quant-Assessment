import os
import requests
import time
from dotenv import load_dotenv

# --- CONFIGURATION ---

# Load the API key from the .env file
load_dotenv()
API_KEY = os.getenv("SEC_API_KEY")

# List of company tickers to get filings for
TICKERS = ["AAPL", "MSFT", "GOOGL", "JPM", "GS", "WMT"]

# Filing types we are interested in.
# Let's add 8-K back in now that we have a fix.
FILING_TYPES = ["10-K", "10-Q", "8-K"]

# Start date for the search (YYYY-MM-DD)
START_DATE = "2022-01-01"

# The folder where we will save the data
DATA_DIR = "data"

# The base URL for the sec-api.io query API
API_URL = "https://api.sec-api.io"

# NEW LINE: Headers to mimic a browser for downloading from sec.gov
DOWNLOAD_HEADERS = {"User-Agent": "MyCoolProject/1.0 name@domain.com"}

# --- SCRIPT ---


def download_filings():
    """
    Downloads SEC filings for a list of tickers and saves them as HTML files.
    """
    if not API_KEY:
        print("Error: SEC_API_KEY not found. Please check your .env file.")
        return

    print("Starting download process...")
    # Create the main data directory if it doesn't exist
    os.makedirs(DATA_DIR, exist_ok=True)

    # Headers for the sec-api.io API call
    api_headers = {"Authorization": API_KEY}

    for ticker in TICKERS:
        print(f"\nProcessing Ticker: {ticker}")

        # Create a subdirectory for the ticker
        ticker_dir = os.path.join(DATA_DIR, ticker)
        os.makedirs(ticker_dir, exist_ok=True)

        # Construct the query for the API
        query = {
            "query": {
                "query_string": {
                    "query": f"ticker:{ticker} AND formType:({' OR '.join(FILING_TYPES)}) AND filedAt:[{START_DATE} TO *]"
                }
            },
            "from": "0",
            "size": "50",
            "sort": [{"filedAt": {"order": "desc"}}],
        }

        # Make the API call to get the list of filings
        try:
            response = requests.post(API_URL, json=query, headers=api_headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching filing list for {ticker}: {e}")
            continue

        filings = response.json().get("filings", [])

        if not filings:
            print(f"No filings found for {ticker} with the specified criteria.")
            continue

        print(f"Found {len(filings)} filings for {ticker}. Downloading...")

        for filing in filings:
            file_url = filing["linkToFilingDetails"]
            form_type = filing["formType"].replace("/", "_")
            filed_at = filing["filedAt"].split("T")[0]

            filename = f"{ticker}_{form_type}_{filed_at}.html"
            filepath = os.path.join(ticker_dir, filename)

            if not os.path.exists(filepath):
                try:
                    time.sleep(1)

                    print(f"  -> Downloading {filename}")

                    # NEW LINE: Use the DOWNLOAD_HEADERS for this request
                    file_response = requests.get(file_url, headers=DOWNLOAD_HEADERS)
                    file_response.raise_for_status()

                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(file_response.text)

                except requests.exceptions.RequestException as e:
                    print(f"    - Could not download {filename}. Reason: {e}")
                except Exception as e:
                    print(
                        f"    - An error occurred while saving {filename}. Reason: {e}"
                    )
            else:
                print(f"  -> Skipping {filename} (already exists)")


if __name__ == "__main__":
    download_filings()
    print("\nDownload process finished.")
