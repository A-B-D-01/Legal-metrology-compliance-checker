// frontend/lib/api.js

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Fallback mock payload for /products/summary when backend is offline
const MOCK_SUMMARY = {
  metrics: {
    totalAudits: 128,
    compliantCount: 94,
    nonCompliantCount: 26,
    pendingReviews: 8,
  },
  recentAudits: [
    {
      id: "1",
      product_name: "Packaged Almond Milk 1L",
      seller_id: "SLR-8921",
      risk: "HIGH",
      status: "MRP Mismatch",
      audited_at: "2026-08-26",
    },
    {
      id: "2",
      product_name: "Organic Honey 500g",
      seller_id: "SLR-4410",
      risk: "LOW",
      status: "Compliant",
      audited_at: "2026-08-25",
    },
    {
      id: "3",
      product_name: "Protein Powder 1kg",
      seller_id: "SLR-1092",
      risk: "MEDIUM",
      status: "Missing Manufacturer Info",
      audited_at: "2026-08-24",
    },
  ],
};

/**
 * Universal fetch wrapper for API endpoints.
 * @param {string} endpoint - API route (e.g. '/products/summary')
 * @param {object} options - Request options (headers, method, body)
 */
export async function apiFetch(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;

  try {
    const res = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!res.ok) {
      throw new Error(`API Error: ${res.status} ${res.statusText}`);
    }

    return await res.json();
  } catch (error) {
    console.warn(`[apiFetch] Request to ${url} failed. Using fallback mock data.`, error);

    // Provide seamless fallback during frontend local testing
    if (endpoint.includes('/products/summary')) {
      return MOCK_SUMMARY;
    }

    // Default fallback structure for other endpoints
    return { success: false, message: error.message };
  }
}