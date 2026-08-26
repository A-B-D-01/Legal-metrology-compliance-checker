import json
from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import (
    GoogleGenerativeAIEmbeddings,
    ChatGoogleGenerativeAI,
)
from langchain_community.vectorstores import FAISS


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv("backend/.env")


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

VECTOR_STORE_PATH = (
    BASE_DIR
    / "vector_stores"
    / "legal_metrology_db"
)


# ============================================================
# LOAD FAISS VECTOR DATABASE
# ============================================================

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


# ============================================================
# SEARCH REGULATIONS
# ============================================================

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


# ============================================================
# COMPLIANCE ANALYSIS
# ============================================================

def analyze_compliance(product_information):
    """
    Search relevant regulations and ask Gemini
    to analyze the product information against them.

    Returns a structured Python dictionary.
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

    # ========================================================
    # GEMINI MODEL
    # ========================================================

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0
    )

    # ========================================================
    # PROMPT
    # ========================================================

    prompt = f"""
You are a Legal Metrology compliance analysis assistant.

Analyze the provided e-commerce product listing ONLY against
the regulatory information supplied below.

CRITICAL RULES:

1. Use ONLY the provided regulatory context.
2. Do NOT invent laws, rules, declarations, penalties,
   requirements, measurements, or recommendations.
3. Do NOT assume something is mandatory unless the
   regulatory context explicitly supports it.
4. If a requirement depends on whether a product is imported,
   clearly mark that condition instead of assuming it.
5. Distinguish between:
   - COMPLIANT
   - NON-COMPLIANT
   - UNCERTAIN
6. If the regulatory context does not provide enough information
   to determine something, mark it as UNCERTAIN.
7. A brand name is NOT automatically the manufacturer name.
8. Do not treat product size such as "Large" as a legal
   declaration unless the provided regulations explicitly say so.
9. Do not create additional requirements that are not present
   in the regulatory context.

REGULATORY CONTEXT
==================
{regulatory_context}

PRODUCT INFORMATION
===================
{product_information}

Return ONLY valid JSON.

Do not use Markdown.
Do not use code fences.
Do not include explanations outside the JSON.

Use exactly this structure:

{{
    "overall_status": "COMPLIANT | NON-COMPLIANT | UNCERTAIN",

    "present_declarations": [
        {{
            "declaration": "string",
            "rule": "string",
            "evidence": "string"
        }}
    ],

    "missing_declarations": [
        {{
            "declaration": "string",
            "rule": "string",
            "reason": "string"
        }}
    ],

    "violations": [
        {{
            "violation": "string",
            "rule": "string",
            "explanation": "string"
        }}
    ],

    "recommendations": [
        "string"
    ]
}}
"""

    # ========================================================
    # CALL GEMINI
    # ========================================================

    response = llm.invoke(prompt)

    raw_response = response.content.strip()

    # ========================================================
    # CLEAN POSSIBLE MARKDOWN CODE FENCES
    # ========================================================

    if raw_response.startswith("```json"):
        raw_response = raw_response[7:]

    elif raw_response.startswith("```"):
        raw_response = raw_response[3:]

    if raw_response.endswith("```"):
        raw_response = raw_response[:-3]

    raw_response = raw_response.strip()

    # ========================================================
    # PARSE JSON
    # ========================================================

    try:

        result = json.loads(raw_response)

        return result

    except json.JSONDecodeError:

        print("\nWARNING: Gemini did not return valid JSON.")

        return {
            "overall_status": "UNCERTAIN",
            "present_declarations": [],
            "missing_declarations": [],
            "violations": [],
            "recommendations": [],
            "raw_analysis": raw_response,
            "error": "Gemini returned an invalid JSON response."
        }


# ============================================================
# DIRECT TERMINAL TEST
# ============================================================

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

    print(json.dumps(
        result,
        indent=4,
        ensure_ascii=False
    ))

    print("\n" + "=" * 60)