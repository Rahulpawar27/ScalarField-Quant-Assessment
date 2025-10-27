# SEC Filings Question-Answering Agent

This project is a complete, end-to-end system built for the Quant Assessment from Scalar Field. It downloads, processes, and indexes SEC filings for major public companies, allowing a user to ask complex, narrative-based questions and receive synthesized, source-cited answers.

## Features

- **Automated Data Pipeline:** Downloads and processes filings for multiple tickers and document types.
- **Advanced Text Cleaning:** Successfully handles and removes complex embedded iXBRL data from HTML filings.
- **RAG Architecture:** Implements a Retrieval-Augmented Generation (RAG) pipeline for question-answering.
- **Semantic Search:** Uses vector embeddings (`all-MiniLM-L6-v2`) and a vector database (`ChromaDB`) to find semantically relevant information.
- **Metadata Filtering:** Intelligently filters searches by company ticker for higher accuracy.
- **Source Attribution:** The final LLM-generated answer cites the specific source document for each piece of information.

## System Architecture

The system follows a standard RAG pipeline:

1.  **Data Ingestion (`download_filings.py`):** Fetches filings from `sec-api.io`.
2.  **Data Processing (`process_all_files.py`):** Cleans HTML and iXBRL, saving clean text.
3.  **Indexing (`bulk_embedder.py`):** Chunks text, creates vector embeddings, and stores them in ChromaDB with metadata.
4.  **Retrieval & Generation (`qa_agent.py`):**
    - Takes a user query.
    - Filters by ticker.
    - Retrieves relevant chunks from ChromaDB.
    - Uses Google's Gemini Pro to synthesize and generate a final, sourced answer.

## Setup Instructions

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd sec_filings_qa
    ```
2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate # On Windows: venv\Scripts\activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Set up API Keys:** Create a `.env` file in the root directory and add your keys:
    ```
    SEC_API_KEY='Your-sec-api.io-Key'
    GOOGLE_API_KEY='Your-Google-AI-Key'
    ```
5.  **Run the pipeline:** Execute the scripts in order:
    ```bash
    python download_filings.py      # Takes a few minutes
    python process_all_files.py     # Takes a few minutes
    python bulk_embedder.py         # Takes 15-30 minutes
    ```

## Usage

Once the pipeline has been run, you can ask questions from the command line. The query must be in quotes.

**Example:**
```bash
python qa_agent.py "What are the main risk factors for Apple?"