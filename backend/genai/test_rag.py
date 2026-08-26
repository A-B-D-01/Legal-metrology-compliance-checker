import os
from pathlib import Path
from dotenv import load_dotenv

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS


# Load environment variables
load_dotenv("backend/.env")


# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
VECTOR_STORE_PATH = BASE_DIR / "vector_stores" / "legal_metrology_db"


def main():
    print("=" * 60)
    print("LEGAL METROLOGY RAG - RETRIEVAL TEST")
    print("=" * 60)

    print("\nLoading Google embedding model...")

    embeddings = GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-001"
    )

    print("Loading FAISS vector database...")

    vector_store = FAISS.load_local(
        str(VECTOR_STORE_PATH),
        embeddings,
        allow_dangerous_deserialization=True
    )

    print("FAISS database loaded successfully!")

    # Test question
    question = input(
        "\nAsk a question about Legal Metrology regulations:\n> "
    )

    print("\nSearching regulatory document...")

    results = vector_store.similarity_search(
        question,
        k=3
    )

    print("\n" + "=" * 60)
    print("RELEVANT REGULATORY INFORMATION")
    print("=" * 60)

    for i, document in enumerate(results, start=1):
        print(f"\n--- Result {i} ---")
        print(document.page_content)

    print("\n" + "=" * 60)
    print("RAG RETRIEVAL TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()