import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS


# Load environment variables
load_dotenv("backend/.env")


# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
VECTOR_STORE_PATH = BASE_DIR / "vector_stores" / "legal_metrology_db"


def load_vector_store():
    """
    Load the FAISS vector database containing
    the Legal Metrology regulations.
    """

    embeddings = GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-001"
    )

    vector_store = FAISS.load_local(
        str(VECTOR_STORE_PATH),
        embeddings,
        allow_dangerous_deserialization=True
    )

    return vector_store


def search_regulations(question, k=3):
    """
    Search the regulatory database for relevant rules.
    """

    vector_store = load_vector_store()

    results = vector_store.similarity_search(
        question,
        k=k
    )

    return results


def analyze_compliance(product_information):
    """
    Search relevant regulations and ask Gemini
    to analyze the product information against them.
    """

    print("\nSearching regulatory database...")

    documents = search_regulations(
        product_information,
        k=5
    )

    regulatory_context = "\n\n".join(
        document.page_content
        for document in documents
    )

    print("Relevant regulations retrieved.")

    # Gemini model
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0
    )

    prompt = f"""
You are a Legal Metrology compliance analysis assistant.

Your task is to analyze an e-commerce product listing
against the provided Indian Legal Metrology regulations.

IMPORTANT:
- Use ONLY the provided regulatory context.
- Do not invent regulations.
- If the provided regulations do not contain enough information,
  clearly say that the information is insufficient.
- Distinguish between compliant, non-compliant, and uncertain items.

REGULATORY CONTEXT:
-------------------
{regulatory_context}
-------------------

PRODUCT INFORMATION:
-------------------
{product_information}
-------------------

Analyze the product and provide:

1. Overall compliance status:
   COMPLIANT / NON-COMPLIANT / UNCERTAIN

2. Mandatory declarations that are present.

3. Mandatory declarations that are missing.

4. Specific violations.

5. Relevant Legal Metrology rule numbers.

6. A short explanation for each violation.

7. Recommended correction.

Return the result in a clear structured format.
"""

    response = llm.invoke(prompt)

    return response.content


if __name__ == "__main__":

    print("=" * 60)
    print("LEGAL METROLOGY RAG - COMPLIANCE ANALYZER")
    print("=" * 60)

    product = input(
        "\nEnter product information:\n> "
    )

    result = analyze_compliance(product)

    print("\n")
    print("=" * 60)
    print("COMPLIANCE ANALYSIS")
    print("=" * 60)

    print(result)

    print("\n" + "=" * 60)