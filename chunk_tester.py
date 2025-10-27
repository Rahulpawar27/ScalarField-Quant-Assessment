import os
from langchain.text_splitter import RecursiveCharacterTextSplitter

# --- CONFIGURATION ---
PROCESSED_DIR = "processed_text"

# IMPORTANT: Change this to a real .txt filename from your processed_text/AAPL folder
FILE_TO_CHUNK = "AAPL_10-K_2024-11-01.txt"
# ---

# Construct the full path to the file
filepath = os.path.join(PROCESSED_DIR, "AAPL", FILE_TO_CHUNK)

print(f"--- Attempting to chunk file: {filepath} ---")

try:
    with open(filepath, "r", encoding="utf-8") as f:
        file_text = f.read()

    # LangChain's text splitter is good at keeping paragraphs/sentences together.
    # chunk_size: The max number of characters in a chunk.
    # chunk_overlap: The number of characters to overlap between chunks. This helps
    #                maintain context between chunks.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )

    # The 'create_documents' method splits the text and returns a list of "Document" objects.
    # Each object contains the text chunk and can hold metadata.
    chunks = text_splitter.create_documents([file_text])

    print(f"\n--- Successfully split the file into {len(chunks)} chunks. ---")

    # Let's look at the first few chunks to see what they look like
    print("\n--- Example of the first 3 chunks: ---\n")
    for i, chunk in enumerate(chunks[:3]):
        print(f"--- CHUNK {i+1} (length: {len(chunk.page_content)}) ---")
        print(chunk.page_content)
        print("\n" + "-" * 40 + "\n")

except FileNotFoundError:
    print(f"\nError: File not found!")
    print(
        f"Please make sure the file '{FILE_TO_CHUNK}' exists in the 'processed_text/AAPL' directory."
    )
except Exception as e:
    print(f"\nAn error occurred: {e}")
