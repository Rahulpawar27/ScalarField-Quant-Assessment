import os
from bs4 import BeautifulSoup
import re  # Import the regular expressions library

# The folder where our data is stored
DATA_DIR = "data"

# --- IMPORTANT ---
# Make sure this is still a real 10-K filename from your data/AAPL folder
FILE_TO_PARSE = "AAPL_10-K_2024-11-01.html"
# ---

# Construct the full path to the file
filepath = os.path.join(DATA_DIR, "AAPL", FILE_TO_PARSE)

print(f"--- Attempting to parse with AGGRESSIVE cleaning: {filepath} ---")

try:
    with open(filepath, "r", encoding="utf-8") as f:
        html_content = f.read()

    # NOTE: We are using the 'lxml' parser now. It's generally faster and better
    # at handling complex/messy HTML and XML-like tags.
    # If you get an error, run: pip install lxml
    soup = BeautifulSoup(html_content, "lxml")

    # --- AGGRESSIVE CLEANING ---

    # 1. Decompose (completely remove) all known iXBRL and other non-textual tags
    #    This is a more comprehensive list.
    tags_to_remove = soup.find_all(
        [
            "ix:nonnumeric",
            "ix:nonfraction",
            "ix:header",
            "ix:continuation",
            "ix:footnote",
            "script",
            "style",
            # Also remove any tag whose name starts with 'ix:' using a regex
            re.compile(r"^ix:.+"),
        ]
    )

    for tag in tags_to_remove:
        tag.decompose()

    # 2. Get the text, which should now be much cleaner
    clean_text = soup.get_text(separator=" ", strip=True)

    # --- END OF CLEANING ---

    print("\n--- First 2000 characters of AGGRESSIVELY cleaned text: ---")
    print(clean_text[:2000])

    print(
        f"\n\n--- Successfully parsed the file. Total characters: {len(clean_text)} ---"
    )

except ImportError:
    print("\nLXML parser not found. Please install it by running:")
    print("pip install lxml")
except FileNotFoundError:
    print(f"\nError: File not found!")
    print(
        f"Please make sure the file '{FILE_TO_PARSE}' exists in the 'data/AAPL' directory."
    )
except Exception as e:
    print(f"\nAn error occurred: {e}")
