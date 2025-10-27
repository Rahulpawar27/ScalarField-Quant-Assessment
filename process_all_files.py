import os
import re
from bs4 import BeautifulSoup
from tqdm import tqdm  # This is the correct way to import for our use case

# --- CONFIGURATION ---

SOURCE_DIR = "data"
TARGET_DIR = "processed_text"

# --- LOGIC ---


def parse_and_clean_html(filepath):
    """
    Opens an HTML filing, cleans it by removing XBRL and other tags,
    and returns the clean narrative text.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            html_content = f.read()

        soup = BeautifulSoup(html_content, "lxml")

        tags_to_remove = soup.find_all(
            [
                "ix:nonnumeric",
                "ix:nonfraction",
                "ix:header",
                "ix:continuation",
                "ix:footnote",
                "script",
                "style",
                re.compile(r"^ix:.+"),
            ]
        )

        for tag in tags_to_remove:
            tag.decompose()

        clean_text = soup.get_text(separator=" ", strip=True)
        return clean_text

    except Exception as e:
        print(f"  - Error processing {os.path.basename(filepath)}: {e}")
        return None


def main():
    """
    Main function to walk through the source directory, process each HTML file,
    and save the clean text to the target directory.
    """
    print(f"Starting bulk processing from '{SOURCE_DIR}' to '{TARGET_DIR}'...")

    os.makedirs(TARGET_DIR, exist_ok=True)

    all_files = []
    for root, _, files in os.walk(SOURCE_DIR):
        for file in files:
            if file.lower().endswith(".html"):
                all_files.append(os.path.join(root, file))

    if not all_files:
        print("No HTML files found to process.")
        return

    # This loop will now work correctly because of the fixed import at the top
    for source_filepath in tqdm(all_files, desc="Processing files"):
        relative_path = os.path.relpath(os.path.dirname(source_filepath), SOURCE_DIR)
        target_subdir = os.path.join(TARGET_DIR, relative_path)
        os.makedirs(target_subdir, exist_ok=True)

        base_filename = os.path.basename(source_filepath)
        target_filename = os.path.splitext(base_filename)[0] + ".txt"
        target_filepath = os.path.join(target_subdir, target_filename)

        if not os.path.exists(target_filepath):
            clean_text = parse_and_clean_html(source_filepath)

            if clean_text:
                try:
                    with open(target_filepath, "w", encoding="utf-8") as f:
                        f.write(clean_text)
                except Exception as e:
                    print(f"  - Error writing to {target_filepath}: {e}")

    print("\nBulk processing finished!")


# --- CORRECTED SCRIPT EXECUTION ---
# Simplified this block to remove the buggy check. Since tqdm is installed,
# we can just call main() directly.
if __name__ == "__main__":
    main()
