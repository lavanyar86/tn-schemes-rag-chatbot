import os
import json
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

load_dotenv()

DATA_PATH = os.path.join("data", "tn_schemes.json")
INDEX_DIR = os.path.join("data", "faiss_index")

def load_scheme_documents():
    """Load scraped scheme records and format them for vector search."""
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Missing {DATA_PATH}. Run scraper.py first.")

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        schemes = json.load(f)

    documents = []
    for scheme in schemes:
        content = (
            f"Scheme Name: {scheme.get('title')}\n"
            f"Department: {scheme.get('department')}\n"
            f"Official Portal: {scheme.get('url')}\n"
            f"Eligibility Criteria: {scheme.get('eligibility', 'N/A')}\n"
            f"Financial & Equipment Benefits: {scheme.get('benefits', 'N/A')}\n"
            f"How to Apply: {scheme.get('application_process', scheme.get('description', 'N/A'))}"
        )

        metadata = {
            "title": scheme.get("title", ""),
            "url": scheme.get("url", ""),
            "department": scheme.get("department", "")
        }

        documents.append(Document(page_content=content, metadata=metadata))

    return documents

def build_faiss_vector_store():
    print("1. Loading scheme documents from json...")
    docs = load_scheme_documents()
    print(f"   Loaded {len(docs)} documents.")

    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        raise ValueError("OPENAI_API_KEY is missing from your .env file!")

    print("2. Generating embeddings using OpenAI text-embedding-3-small...")
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=openai_key
    )

    print("3. Building and indexing into FAISS vector database...")
    vectorstore = FAISS.from_documents(docs, embeddings)

    # Save FAISS index locally to disk
    vectorstore.save_local(INDEX_DIR)
    print(f"   FAISS vector database successfully saved to: {INDEX_DIR}")
    return vectorstore

if __name__ == "__main__":
    build_faiss_vector_store()