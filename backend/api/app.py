from fastapi import FastAPI
from pydantic import BaseModel

from backend.genai.rag import analyze_compliance


app = FastAPI(
    title="Legal Metrology Compliance Checker",
    description="AI-powered Legal Metrology compliance analysis API",
    version="1.0.0"
)


class ProductRequest(BaseModel):
    product: str
    brand: str | None = None
    size: str | None = None
    material: str | None = None
    price: str | None = None


@app.get("/")
def root():
    return {
        "message": "Legal Metrology Compliance Checker API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


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