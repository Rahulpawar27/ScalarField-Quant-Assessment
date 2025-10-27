import os
import chromadb
from langchain.text_splitter import RecursiveCharacterTextSplitter

# --- CONFIGURATION ---
PROCESSED_DIR = "processed_text"
DB_DIR = "chroma_db"
COLLECTION_NAME = "sec_filings"

# IMPORTANT: Change this to a real .txt filename from your processed_text/AAPL folder
FILE_TO_EMBED = "AAPL_10-K_2024-11-01.txt"
# ---

# Get the absolute path for the database directory
db_path = os.path.abspath(DB_DIR)

print(f"--- Setting up ChromaDB client at: {db_path} ---")

# 1. Set up the ChromaDB client with persistent storage
client = chromadb.PersistentClient(path=db_path)

# 2. Get or create the collection. This is like a table in a regular database.
#    The first time this runs, it will download the embedding model ('all-MiniLM-L6-v2')
#    which may take a minute.
collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    metadata={"hnsw:space": "cosine"},  # Using cosine distance for similarity
)

# 3. Load and chunk the document
try:
    filepath = os.path.join(PROCESSED_DIR, "AAPL", FILE_TO_EMBED)
    print(f"--- Loading and chunking file: {FILE_TO_EMBED} ---")

    with open(filepath, "r", encoding="utf-8") as f:
        file_text = f.read()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.create_documents([file_text])

    # Prepare data for ChromaDB
    documents = [chunk.page_content for chunk in chunks]

    # --- CRITICAL STEP: Create metadata for each chunk ---
    # We get this from the filename itself.
    base_filename = os.path.splitext(FILE_TO_EMBED)[0]
    ticker, form_type, date = base_filename.split("_")

    metadatas = [
        {
            "ticker": ticker,
            "form_type": form_type,
            "date": date,
            "source_file": FILE_TO_EMBED,
        }
        for _ in documents
    ]

    # Create unique IDs for each chunk
    ids = [f"{base_filename}_chunk_{i}" for i in range(len(documents))]

    # 4. Add the documents to the collection
    #    ChromaDB will automatically handle the embedding process for us.
    print(
        f"\n--- Adding {len(documents)} chunks to the '{COLLECTION_NAME}' collection... ---"
    )
    collection.add(documents=documents, metadatas=metadatas, ids=ids)

    print("\n--- Successfully embedded and stored the document chunks. ---")
    print(f"--- Total items in collection: {collection.count()} ---")

except FileNotFoundError:
    print(f"\nError: File not found! Please check the filename and path.")
except Exception as e:
    print(f"\nAn error occurred: {e}")
