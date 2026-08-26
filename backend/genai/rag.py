import json
from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import (
    GoogleGenerativeAIEmbeddings,
    ChatGoogleGenerativeAI,
)
from langchain_community.vectorstores import FAISS


# ============================================================
# ENVIRONMENT
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
    Indian Legal Metrology regulations.
    """

    embeddings = GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-001"
    )

    vector_store = FAISS.load_local(
        str(VECTOR_STORE_PATH),
        embeddings,
        allow_dangerous_deserialization=True,
    )

    return vector_store


# ============================================================
# SEARCH REGULATIONS
# ============================================================

def search_regulations(question, k=5):
    """
    Search the Legal Metrology regulatory database
    for the most relevant regulatory information.
    """

    vector_store = load_vector_store()

    results = vector_store.similarity_search(
        question,
        k=k,
    )

    return results


# ============================================================
# COMPLIANCE ANALYSIS
# ============================================================

def analyze_compliance(product_information):
    """
    Analyze an e-commerce product listing against
    relevant Indian Legal Metrology requirements.

    The analysis is intentionally restricted to the
    mandatory declarations that can currently be
    evaluated from the product information supplied
    through the API.
    """

    print("\nSearching regulatory database...")

    # --------------------------------------------------------
    # Retrieve relevant regulations using FAISS
    # --------------------------------------------------------

    documents = search_regulations(
        product_information,
        k=5,
    )

    if not documents:
        raise RuntimeError(
            "No relevant regulatory information was found."
        )

    regulatory_context = "\n\n".join(
        document.page_content
        for document in documents
    )

    print("Relevant regulations retrieved.")

    # --------------------------------------------------------
    # Gemini model
    # --------------------------------------------------------

    print("Sending request to Gemini...")

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        max_retries=1,
    )

    # --------------------------------------------------------
    # Compliance prompt
    # --------------------------------------------------------

    prompt = f"""
You are an Indian Legal Metrology compliance analysis assistant.

Your job is to analyze an e-commerce product listing against
ONLY the regulatory context provided below.

The current system is checking PRODUCT INFORMATION only.

Do NOT perform physical package/image analysis.

============================================================
IMPORTANT INSTRUCTIONS
============================================================

1. Use ONLY the provided regulatory context.

2. Do NOT invent:
   - rules
   - rule numbers
   - penalties
   - requirements
   - legal provisions

3. Do NOT assume that a brand name is the manufacturer,
   packer, or importer.

4. Analyze ONLY these six declaration categories:

   A. Manufacturer / Packer / Importer
      Relevant rules:
      Rule 6(a), Rule 6(aa)

   B. Country of Origin
      Relevant rule:
      Rule 6(aa)
      This is conditional and applies when the product
      is imported.

   C. Common or Generic Name of Commodity
      Relevant rule:
      Rule 6(b)

   D. Net Quantity
      Relevant rule:
      Rule 6(c)

   E. Month and Year of Manufacture
      Relevant rule:
      Rule 6(d)

   F. Retail Sale Price / MRP
      Relevant rule:
      Rule 6(e)

5. Do NOT analyze or return results for:
   - Rule 9 visibility
   - Rule 9 contrast
   - Rule 9 legibility
   - Rule 9 language
   - handwritten declarations
   - liquid obstruction
   - Rule 11 packaging exclusion
   - Rule 25 MRP alteration
   - grouped packages
   - outer packaging
   - promotional package rules
   - physical package placement
   - visual/image-based compliance

6. These excluded requirements will be handled later by
   other parts of the system, such as the computer vision
   module.

7. Distinguish carefully between:

   PRESENT
   The product information explicitly provides the required
   declaration.

   MISSING
   The requirement clearly applies and the required
   information is clearly absent.

   UNCERTAIN
   The requirement depends on information that has not been
   provided.

8. If Country of Origin depends on whether the product is
   imported and the product information does not tell you
   whether it is imported, classify Country of Origin as
   UNCERTAIN.

9. Do NOT classify Country of Origin as a violation unless
   the product is clearly identified as imported.

10. Do NOT assume "Brand" is equivalent to manufacturer.

11. "Size: Large" must NOT automatically be treated as a
    legal net quantity declaration.

12. A product size such as "Large", "XL", "Medium", etc.
    is not by itself evidence of net quantity.

13. If the product information clearly contains a declaration,
    put it in present_declarations.

14. If a mandatory declaration is clearly absent, put it in
    missing_declarations.

15. Only put something in violations when the information
    clearly demonstrates a failure to satisfy a requirement.

16. Recommendations must only address the six declaration
    categories listed above.

17. Keep the answer specific to the supplied product.

18. Return ONLY valid JSON.

19. Do NOT use Markdown.

20. Do NOT wrap the JSON in ```json or ```.

============================================================
REGULATORY CONTEXT
============================================================

{regulatory_context}

============================================================
PRODUCT INFORMATION
============================================================

{product_information}

============================================================
REQUIRED JSON STRUCTURE
============================================================

Return exactly this structure:

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

    "uncertain_declarations": [
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

============================================================
OVERALL STATUS LOGIC
============================================================

Use:

COMPLIANT
Only when all applicable six declaration categories are
satisfied and there are no clear violations.

NON-COMPLIANT
When at least one applicable mandatory declaration is
clearly missing or violated.

UNCERTAIN
When there is not enough information to determine whether
the applicable requirements are satisfied and there are no
clear violations.

If there is at least one clear violation or missing mandatory
declaration, the overall status should normally be
NON-COMPLIANT even if other declarations are uncertain.

============================================================
FINAL VALIDATION
============================================================

Before returning the response:

- Return valid JSON only.
- Make sure all six declaration categories were considered.
- Do not return excluded Rule 9, Rule 11, or Rule 25 checks.
- Do not invent rule numbers.
- Do not treat Brand as Manufacturer.
- Do not treat Size as Net Quantity.
- Do not automatically require Country of Origin unless the
  product is clearly imported.
- Use UNCERTAIN when required information is unavailable.
- Keep recommendations relevant to the six categories.
"""


    # --------------------------------------------------------
    # Call Gemini
    # --------------------------------------------------------

    print("Waiting for Gemini response...")

    response = llm.invoke(prompt)

    print("Gemini response received.")

    content = response.content

    # --------------------------------------------------------
    # Clean Gemini response
    # --------------------------------------------------------

    content = content.strip()

    if content.startswith("```json"):
        content = content[len("```json"):].strip()

    elif content.startswith("```"):
        content = content[len("```"):].strip()

    if content.endswith("```"):
        content = content[:-3].strip()

    # --------------------------------------------------------
    # Convert Gemini response to Python dictionary
    # --------------------------------------------------------

    try:
        result = json.loads(content)

    except json.JSONDecodeError:

        return {
            "overall_status": "UNCERTAIN",
            "present_declarations": [],
            "missing_declarations": [],
            "uncertain_declarations": [],
            "violations": [],
            "recommendations": [],
            "raw_analysis": content,
        }

    # --------------------------------------------------------
    # Basic structure validation
    # --------------------------------------------------------

    required_keys = [
        "overall_status",
        "present_declarations",
        "missing_declarations",
        "uncertain_declarations",
        "violations",
        "recommendations",
    ]

    for key in required_keys:
        if key not in result:
            result[key] = []

    # Ensure overall_status is valid
    if result["overall_status"] not in [
        "COMPLIANT",
        "NON-COMPLIANT",
        "UNCERTAIN",
    ]:
        result["overall_status"] = "UNCERTAIN"

    return result


# ============================================================
# COMMAND LINE TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("LEGAL METROLOGY RAG - COMPLIANCE ANALYZER")
    print("=" * 60)

    product = input(
        "\nEnter product information:\n> "
    )

    try:

        result = analyze_compliance(product)

        print("\n")
        print("=" * 60)
        print("COMPLIANCE ANALYSIS")
        print("=" * 60)

        print(
            json.dumps(
                result,
                indent=4,
                ensure_ascii=False,
            )
        )

        print("\n" + "=" * 60)

    except KeyboardInterrupt:

        print("\n\nAnalysis cancelled by user.")

    except Exception as error:

        print("\nERROR:")
        print(error)