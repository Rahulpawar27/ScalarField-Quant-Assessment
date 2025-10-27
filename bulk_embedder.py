import os
import chromadb
from langchain.text_splitter import RecursiveCharacterTextSplitter
from tqdm import tqdm

# --- CONFIGURATION ---
PROCESSED_DIR = "processed_text"
DB_DIR = "chroma_db"
COLLECTION_NAME = "sec_filings"
# ---


def main():
    """
    Main function to chunk, embed, and store all processed text files
    into the ChromaDB vector database.
    """
    # 1. Set up ChromaDB client and collection
    client = chromadb.PersistentClient(path=os.path.abspath(DB_DIR))
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
    )

    print("Starting bulk embedding process...")

    # 2. Get a list of all .txt files to process
    all_text_files = []
    for root, _, files in os.walk(PROCESSED_DIR):
        for file in files:
            if file.lower().endswith(".txt"):
                all_text_files.append(os.path.join(root, file))

    if not all_text_files:
        print("No .txt files found to process.")
        return

    # 3. Process each file with a progress bar
    for filepath in tqdm(all_text_files, desc="Embedding files"):
        filename = os.path.basename(filepath)

        # Check if the document has already been processed and added
        # We query by source_file metadata to check for existence
        existing_docs = collection.get(where={"source_file": filename})
        if len(existing_docs["ids"]) > 0:
            # print(f"Skipping {filename} as it already exists in the collection.")
            continue

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                file_text = f.read()

            # Chunk the document
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, chunk_overlap=200
            )
            chunks = text_splitter.create_documents([file_text])

            documents = [chunk.page_content for chunk in chunks]

            # Create metadata and IDs
            base_filename = os.path.splitext(filename)[0]
            parts = base_filename.split("_")
            if len(parts) < 3:
                # print(f"Skipping malformed filename: {filename}")
                continue
            ticker, form_type, date = parts[0], parts[1], parts[2]

            metadatas = [
                {
                    "ticker": ticker,
                    "form_type": form_type,
                    "date": date,
                    "source_file": filename,
                }
                for _ in documents
            ]

            ids = [f"{base_filename}_chunk_{i}" for i in range(len(documents))]

            # Add to collection if there are any documents to add
            if documents:
                collection.add(documents=documents, metadatas=metadatas, ids=ids)

        except Exception as e:
            print(f"\nError processing {filename}: {e}")

    print("\nBulk embedding finished!")
    print(f"--- Total items in collection: {collection.count()} ---")


if __name__ == "__main__":
    main()
