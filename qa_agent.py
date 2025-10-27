import os
import chromadb
import argparse
import google.generativeai as genai
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv()
DB_DIR = "chroma_db"
COLLECTION_NAME = "sec_filings"
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# NEW: A map to connect company names to tickers for better recognition
COMPANY_MAP = {
    "apple": "AAPL",
    "microsoft": "MSFT",
    "google": "GOOGL",
    "alphabet": "GOOGL",
    "jpmorgan chase": "JPM",
    "jpmorgan": "JPM",
    "chase": "JPM",
    "goldman sachs": "GS",
    "walmart": "WMT",
}
# ---


def smart_ticker_extraction(query):
    """Smarter method to find a ticker using a company name map."""
    query_lower = query.lower()
    for name, ticker in COMPANY_MAP.items():
        if name in query_lower:
            return ticker
    return None


def generate_response(context, query):
    """Generates a response using the Gemini LLM based on the provided context."""
    if not GOOGLE_API_KEY:
        return "Error: GOOGLE_API_KEY not found. Please set it in your .env file."

    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = f"""
        You are a helpful financial analyst assistant. Your task is to answer the user's question based *only* on the provided context from SEC filings.

        Follow these rules:
        1.  Synthesize the information from the context into a clear, concise answer.
        2.  Do not add any information that is not present in the context.
        3.  If the context does not contain the answer, state "I could not find an answer to your question in the provided documents."
        4.  Cite the sources used in your answer by referencing the source file (e.g., "According to [source_file], ...").

        CONTEXT:
        ---
        {context}
        ---

        QUESTION: {query}

        ANSWER:
        """

        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        return f"An error occurred during generation: {e}"


def main(query_text, num_results=7):
    """
    Main function to filter, query the vector database, and generate a response.
    """
    client = chromadb.PersistentClient(path=os.path.abspath(DB_DIR))
    collection = client.get_collection(name=COLLECTION_NAME)

    # --- CORRECTED FILTER LOGIC ---
    # Initialize filter to None
    ticker_filter = None
    extracted_ticker = smart_ticker_extraction(query_text)
    if extracted_ticker:
        # Only create the filter dictionary if a ticker is found
        ticker_filter = {"ticker": extracted_ticker}
        print(f"--- Filtering results for ticker: {extracted_ticker} ---")
    else:
        print("--- No specific company found in query, searching all documents. ---")

    # The 'where' parameter can now correctly handle 'None'
    results = collection.query(
        query_texts=[query_text],
        n_results=num_results,
        where=ticker_filter if ticker_filter else None,
    )
    # --- END OF CORRECTIONS ---

    documents = results["documents"][0]
    if not documents:
        print("No relevant documents found for your query.")
        return

    context = ""
    for i, doc in enumerate(documents):
        metadata = results["metadatas"][0][i]
        context += f"Source File: {metadata['source_file']}\nContent: {doc}\n\n---\n\n"

    print("\n--- Generating final answer... ---\n")
    final_answer = generate_response(context, query_text)
    print(final_answer)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Query the SEC Filings knowledge base."
    )
    parser.add_argument("query", type=str, help="The question you want to ask.")
    parser.add_argument(
        "-n",
        "--num_results",
        type=int,
        default=7,
        help="Number of context chunks to retrieve.",
    )

    args = parser.parse_args()
    main(args.query, args.num_results)
