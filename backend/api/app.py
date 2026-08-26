from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.genai.rag import analyze_compliance


app = FastAPI(
    title="Legal Metrology Compliance Checker",
    description="AI-powered Legal Metrology compliance analysis API",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST MODEL
# ============================================================

class ProductRequest(BaseModel):
    product: str
    brand: str | None = None
    size: str | None = None
    material: str | None = None
    price: str | None = None


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "Legal Metrology Compliance Checker API is running"
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# ============================================================
# COMPLIANCE CHECK
# ============================================================

@app.post("/api/compliance/check")
def check_compliance(request: ProductRequest):

    product_information = f"""
Product: {request.product}
Brand: {request.brand or "Not provided"}
Size: {request.size or "Not provided"}
Material: {request.material or "Not provided"}
Price: {request.price or "Not provided"}
"""

    result = analyze_compliance(product_information)

    return {
        "success": True,
        "product": request.product,
        "analysis": result
    }