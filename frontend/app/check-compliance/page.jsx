"use client";

import { useState } from "react";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export default function CheckCompliancePage() {
  const [form, setForm] = useState({
    product: "",
    brand: "",
    size: "",
    material: "",
    price: "",
  });

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    setLoading(true);
    setResult(null);
    setError(null);

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/compliance/check`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(form),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail
            ? JSON.stringify(data.detail)
            : `Request failed with status ${response.status}`
        );
      }

      if (!data.success) {
        throw new Error(data.message || "Compliance analysis failed.");
      }

      setResult(data);
    } catch (err) {
      console.error("Compliance API error:", err);
      setError(err.message || "Unable to connect to the backend.");
    } finally {
      setLoading(false);
    }
  };

  const analysis = result?.analysis;

  const statusClass =
    analysis?.overall_status === "COMPLIANT"
      ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30"
      : analysis?.overall_status === "UNCERTAIN"
        ? "bg-yellow-500/10 text-yellow-400 border-yellow-500/30"
        : "bg-red-500/10 text-red-400 border-red-500/30";

  return (
    <div className="max-w-5xl mx-auto space-y-8 pb-12">

      {/* Header */}
      <div>
        <h1 className="text-3xl font-extrabold text-white tracking-tight">
          Audit Engine
        </h1>

        <p className="text-zinc-400 text-sm mt-1">
          Analyze e-commerce product information against Indian Legal
          Metrology regulations using FAISS RAG and Gemini AI.
        </p>
      </div>

      {/* Input Form */}
      <div className="bg-zinc-900/90 backdrop-blur-2xl p-6 rounded-2xl border border-zinc-800 shadow-[0_0_50px_rgba(0,0,0,0.8)] relative">

        <div className="absolute top-0 left-1/4 w-32 h-[2px] bg-gradient-to-r from-transparent via-cyan-500 to-transparent" />

        <form onSubmit={handleSubmit} className="space-y-5">

          {/* Product */}
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-zinc-400 mb-2">
              Product Name
            </label>

            <input
              type="text"
              name="product"
              required
              placeholder="e.g. Cotton T-Shirt"
              value={form.product}
              onChange={handleChange}
              className="w-full px-4 py-3 bg-zinc-950 border border-zinc-800 rounded-xl text-white placeholder-zinc-600 focus:outline-none focus:border-cyan-500 text-sm transition-all"
            />
          </div>

          {/* Brand */}
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-zinc-400 mb-2">
              Brand
            </label>

            <input
              type="text"
              name="brand"
              placeholder="e.g. ABC"
              value={form.brand}
              onChange={handleChange}
              className="w-full px-4 py-3 bg-zinc-950 border border-zinc-800 rounded-xl text-white placeholder-zinc-600 focus:outline-none focus:border-cyan-500 text-sm transition-all"
            />
          </div>

          {/* Size */}
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-zinc-400 mb-2">
              Size
            </label>

            <input
              type="text"
              name="size"
              placeholder="e.g. Large"
              value={form.size}
              onChange={handleChange}
              className="w-full px-4 py-3 bg-zinc-950 border border-zinc-800 rounded-xl text-white placeholder-zinc-600 focus:outline-none focus:border-cyan-500 text-sm transition-all"
            />
          </div>

          {/* Material */}
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-zinc-400 mb-2">
              Material
            </label>

            <input
              type="text"
              name="material"
              placeholder="e.g. 100% Cotton"
              value={form.material}
              onChange={handleChange}
              className="w-full px-4 py-3 bg-zinc-950 border border-zinc-800 rounded-xl text-white placeholder-zinc-600 focus:outline-none focus:border-cyan-500 text-sm transition-all"
            />
          </div>

          {/* Price */}
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-zinc-400 mb-2">
              Price / MRP
            </label>

            <input
              type="text"
              name="price"
              placeholder="e.g. Rs. 499"
              value={form.price}
              onChange={handleChange}
              className="w-full px-4 py-3 bg-zinc-950 border border-zinc-800 rounded-xl text-white placeholder-zinc-600 focus:outline-none focus:border-cyan-500 text-sm transition-all"
            />
          </div>

          {/* Submit */}
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3.5 bg-gradient-to-r from-cyan-500 to-teal-500 hover:from-cyan-400 hover:to-teal-400 text-zinc-950 font-bold uppercase tracking-wider text-xs rounded-xl shadow-lg shadow-cyan-950/50 transition-all active:scale-[0.98] disabled:opacity-50"
          >
            {loading
              ? "Analyzing with AI..."
              : "Run Compliance Audit"}
          </button>
        </form>
      </div>

      {/* Error */}
      {error && (
        <div className="p-4 bg-red-950/60 border border-red-500/50 text-red-200 text-sm rounded-2xl shadow-lg">
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Results */}
      {analysis && (
        <div className="space-y-6">

          {/* Overall Status */}
          <div className="bg-zinc-900/90 backdrop-blur-2xl p-6 rounded-2xl border border-zinc-800 shadow-2xl">

            <div className="flex justify-between items-center border-b border-zinc-800 pb-4">

              <div>
                <h2 className="text-lg font-bold text-white tracking-wide">
                  Compliance Report
                </h2>

                <p className="text-xs text-zinc-500 mt-1">
                  {result.product}
                </p>
              </div>

              <span
                className={`px-4 py-2 text-xs font-bold rounded-full uppercase tracking-wider border ${statusClass}`}
              >
                {analysis.overall_status}
              </span>
            </div>
          </div>

          {/* Present Declarations */}
          <ResultSection
            title="Present Declarations"
            items={analysis.present_declarations}
            type="present"
          />

          {/* Missing Declarations */}
          <ResultSection
            title="Missing Declarations"
            items={analysis.missing_declarations}
            type="missing"
          />

          {/* Uncertain Declarations */}
          <ResultSection
            title="Uncertain Declarations"
            items={analysis.uncertain_declarations}
            type="uncertain"
          />

          {/* Violations */}
          <ResultSection
            title="Violations"
            items={analysis.violations}
            type="violation"
          />

          {/* Recommendations */}
          {analysis.recommendations?.length > 0 && (
            <div className="bg-zinc-900/90 backdrop-blur-2xl p-6 rounded-2xl border border-zinc-800 shadow-2xl">

              <h2 className="text-sm font-bold text-white uppercase tracking-wider mb-4">
                Recommended Corrections
              </h2>

              <div className="space-y-3">
                {analysis.recommendations.map((recommendation, index) => (
                  <div
                    key={index}
                    className="flex gap-3 text-sm text-zinc-300"
                  >
                    <span className="text-cyan-400 font-bold">
                      {index + 1}.
                    </span>

                    <span>{recommendation}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}


/* ============================================================
   RESULT SECTION
============================================================ */

function ResultSection({ title, items, type }) {
  if (!items || items.length === 0) {
    return null;
  }

  const borderClass =
    type === "present"
      ? "border-emerald-500/20"
      : type === "missing" || type === "violation"
        ? "border-red-500/20"
        : "border-yellow-500/20";

  return (
    <div
      className={`bg-zinc-900/90 backdrop-blur-2xl p-6 rounded-2xl border ${borderClass} shadow-2xl`}
    >
      <h2 className="text-sm font-bold text-white uppercase tracking-wider mb-4">
        {title}
      </h2>

      <div className="space-y-4">
        {items.map((item, index) => (
          <div
            key={index}
            className="bg-zinc-950/70 border border-zinc-800 rounded-xl p-4"
          >

            <div className="flex justify-between gap-4">

              <h3 className="text-sm font-semibold text-white">
                {item.declaration ||
                  item.violation ||
                  "Compliance Finding"}
              </h3>

              {item.rule && (
                <span className="text-xs text-cyan-400 whitespace-nowrap">
                  {item.rule}
                </span>
              )}
            </div>

            {item.evidence && (
              <p className="text-xs text-zinc-400 mt-2">
                <span className="text-zinc-500">Evidence:</span>{" "}
                {item.evidence}
              </p>
            )}

            {item.reason && (
              <p className="text-xs text-zinc-400 mt-2 leading-relaxed">
                <span className="text-zinc-500">Reason:</span>{" "}
                {item.reason}
              </p>
            )}

            {item.explanation && (
              <p className="text-xs text-zinc-400 mt-2 leading-relaxed">
                <span className="text-zinc-500">Explanation:</span>{" "}
                {item.explanation}
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}