"""
compliance_engine.py — MetaMark AI/ML Developer (Dev 4) deliverable
=====================================================================
ALL-IN-ONE FILE: engine + sample data + tests, in one place.

No pip installs needed — uses only Python's built-in libraries.

HOW TO RUN:
    python compliance_engine.py

That's it. It will run all the tests at the bottom and print PASS/FAIL.
"""

from __future__ import annotations

import json
import logging
import re
import time
import unittest
from dataclasses import dataclass, field
from typing import Any, Callable, Optional
from unittest.mock import MagicMock

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("metamark.ai_vision.compliance_engine")


# =========================================================================
# 1. THE 9 MANDATORY LEGAL METROLOGY DECLARATIONS
# =========================================================================
MANDATORY_FIELDS: list[str] = [
    "mrp",
    "net_quantity",
    "manufacturer_name_address",
    "country_of_origin",
    "date_of_manufacture_or_packing",
    "consumer_care_details",
    "batch_or_lot_number",
    "best_before_or_expiry",
    "unit_sale_price",
]

FIELD_LABELS: dict[str, str] = {
    "mrp": "Maximum Retail Price (MRP)",
    "net_quantity": "Net quantity (with correct unit)",
    "manufacturer_name_address": "Manufacturer / packer / importer name & address",
    "country_of_origin": "Country of origin",
    "date_of_manufacture_or_packing": "Date of manufacture or packing",
    "consumer_care_details": "Consumer care / customer support details",
    "batch_or_lot_number": "Batch or lot number",
    "best_before_or_expiry": "Best-before / expiry date",
    "unit_sale_price": "Unit sale price (for combination packs)",
    "ingredients": "Ingredients / composition list",
    "fssai_number": "FSSAI license number",
    "bis_certification": "BIS certification mark",
    "isbn": "ISBN",
}

CATEGORY_RULE_PACKS: dict[str, dict[str, Any]] = {
    "food": {
        "extra_required": ["ingredients", "fssai_number"],
        "waived": [],
        "expiry_required": True,
    },
    "skincare": {
        "extra_required": ["ingredients"],
        "waived": [],
        "expiry_required": True,
    },
    "electric": {
        "extra_required": ["bis_certification"],
        "waived": ["best_before_or_expiry"],
        "expiry_required": False,
    },
    "book": {
        "extra_required": ["isbn"],
        "waived": ["best_before_or_expiry", "batch_or_lot_number"],
        "expiry_required": False,
    },
    "general": {
        "extra_required": [],
        "waived": ["best_before_or_expiry"],
        "expiry_required": False,
    },
}

VALID_CATEGORIES = set(CATEGORY_RULE_PACKS)


def _rule_pack_for(category: str) -> dict[str, Any]:
    return CATEGORY_RULE_PACKS.get(category, CATEGORY_RULE_PACKS["general"])


def required_fields_for_category(category: str) -> list[str]:
    """Full list of fields this category must declare (base 9 + extras - waived)."""
    pack = _rule_pack_for(category)
    fields = [f for f in MANDATORY_FIELDS if f not in pack["waived"]]
    fields += [f for f in pack["extra_required"] if f not in fields]
    return fields


# =========================================================================
# 2. RETRY LOGIC FOR EXTERNAL API CALLS (Vision / Gemini)
# =========================================================================

class TransientAPIError(Exception):
    """Raised by the vision/LLM client wrappers on rate limits or timeouts."""


def with_retries(
    max_attempts: int = 3,
    base_delay_seconds: float = 1.0,
    retry_on: tuple[type[Exception], ...] = (TransientAPIError,),
):
    """
    Decorator adding exponential-backoff retries around flaky external calls
    (Google Vision OCR, Gemini).
    """

    def decorator(fn: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            last_exc: Optional[Exception] = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return fn(*args, **kwargs)
                except retry_on as exc:  # type: ignore[misc]
                    last_exc = exc
                    if attempt == max_attempts:
                        break
                    delay = base_delay_seconds * (2 ** (attempt - 1))
                    logger.warning(
                        "%s failed (attempt %d/%d): %s — retrying in %.1fs",
                        fn.__name__, attempt, max_attempts, exc, delay,
                    )
                    time.sleep(delay)
            logger.error("%s failed after %d attempts: %s", fn.__name__, max_attempts, last_exc)
            raise last_exc

        return wrapper

    return decorator


def _strip_json_fence(raw: str) -> str:
    """
    Gemini frequently wraps JSON in markdown fences, sometimes with a language
    tag, sometimes with leading/trailing prose. Handle every variant.
    """
    if raw is None:
        return ""
    text = raw.strip()

    fence_match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
    if fence_match:
        return fence_match.group(1).strip()

    first_brace = min(
        (i for i in (text.find("{"), text.find("[")) if i != -1),
        default=-1,
    )
    if first_brace > 0:
        text = text[first_brace:]

    last_close = max(text.rfind("}"), text.rfind("]"))
    if last_close != -1:
        text = text[: last_close + 1]

    return text.strip()


def safe_json_loads(raw: str, default: Any = None) -> Any:
    """Parse a (possibly fenced/messy) LLM JSON response without raising."""
    cleaned = _strip_json_fence(raw)
    try:
        return json.loads(cleaned)
    except (json.JSONDecodeError, TypeError):
        logger.warning("Could not parse JSON from model response: %r", raw[:200] if raw else raw)
        return default


# =========================================================================
# 3. NORMALIZING MESSY HUMAN INPUT (the old sensor fields, now typed by hand)
# =========================================================================

_WEIGHT_UNIT_TO_GRAMS = {
    "g": 1.0, "gm": 1.0, "gms": 1.0, "gram": 1.0, "grams": 1.0,
    "kg": 1000.0, "kgs": 1000.0, "kilogram": 1000.0, "kilograms": 1000.0,
    "mg": 0.001,
    "ml": 1.0, "l": 1000.0, "lt": 1000.0, "ltr": 1000.0,
}

_WEIGHT_PATTERN = re.compile(r"^\s*([\d]*\.?\d+)\s*([a-zA-Z]+)\s*\.?\s*$")

_DIMENSION_TRIPLE_PATTERN = re.compile(
    r"([\d]*\.?\d+)\s*(cm|mm|m|in|inch|inches)?\s*[x×]\s*"
    r"([\d]*\.?\d+)\s*(cm|mm|m|in|inch|inches)?\s*[x×]\s*"
    r"([\d]*\.?\d+)\s*(cm|mm|m|in|inch|inches)?",
    re.IGNORECASE,
)

_DIMENSION_LABELLED_PATTERN = re.compile(
    r"length\s*:?\s*([\d]*\.?\d+)\s*(cm|mm|m|in|inch|inches)?.*?"
    r"width\s*:?\s*([\d]*\.?\d+)\s*(cm|mm|m|in|inch|inches)?.*?"
    r"height\s*:?\s*([\d]*\.?\d+)\s*(cm|mm|m|in|inch|inches)?",
    re.IGNORECASE | re.DOTALL,
)

_LENGTH_UNIT_TO_CM = {
    "cm": 1.0, "mm": 0.1, "m": 100.0, "in": 2.54, "inch": 2.54, "inches": 2.54,
}


def normalize_weight_to_grams(raw: Optional[str]) -> Optional[float]:
    """
    Parse a human-typed weight string into grams.
    Returns None (not an exception) for blank/unparseable input.

    Handles: "250g", "0.25kg", "250 g", "1 KG", "  ", None, "abc123xyz"
    """
    if not raw or not str(raw).strip():
        return None

    text = str(raw).strip().lower().replace(",", "")
    match = _WEIGHT_PATTERN.match(text)
    if not match:
        logger.info("normalize_weight_to_grams: unparseable input %r", raw)
        return None

    value_str, unit = match.groups()
    unit = unit.strip().lower()
    factor = _WEIGHT_UNIT_TO_GRAMS.get(unit)
    if factor is None:
        logger.info("normalize_weight_to_grams: unknown unit %r in %r", unit, raw)
        return None

    try:
        return round(float(value_str) * factor, 3)
    except ValueError:
        return None


def normalize_dimensions_to_cm(raw: Optional[str]) -> Optional[tuple[float, float, float]]:
    """
    Parse a human-typed dimension string into (length_cm, width_cm, height_cm).
    Returns None for blank/unparseable input.

    Handles: "15x10x5cm", "15 cm x 10 cm x 5cm", "15CM X 10CM X 5CM",
    "Length: 15cm, Width: 10cm, Height: 5cm", None, "", "not measured"
    """
    if not raw or not str(raw).strip():
        return None

    text = str(raw).strip()

    match = _DIMENSION_TRIPLE_PATTERN.search(text)
    if not match:
        match = _DIMENSION_LABELLED_PATTERN.search(text)

    if not match:
        logger.info("normalize_dimensions_to_cm: unparseable input %r", raw)
        return None

    groups = match.groups()
    values_and_units = [(groups[0], groups[1]), (groups[2], groups[3]), (groups[4], groups[5])]

    cm_values = []
    default_unit = "cm"
    named_units = [u for _, u in values_and_units if u]
    if named_units:
        default_unit = named_units[-1].lower()

    for value_str, unit in values_and_units:
        unit = (unit or default_unit).lower()
        factor = _LENGTH_UNIT_TO_CM.get(unit, 1.0)
        try:
            cm_values.append(round(float(value_str) * factor, 3))
        except ValueError:
            return None

    return tuple(cm_values)  # type: ignore[return-value]


# =========================================================================
# 4. DATA MODELS
# =========================================================================

@dataclass
class Violation:
    field: str
    severity: str  # "critical" | "major" | "minor"
    message: str
    suggested_fix: str


@dataclass
class ComplianceResult:
    product_id: Optional[str]
    category: str
    score: float
    grade: str
    violations: list[Violation] = field(default_factory=list)
    declared_fields: dict[str, Any] = field(default_factory=dict)
    actual_weight_grams: Optional[float] = None
    actual_dimensions_cm: Optional[tuple[float, float, float]] = None
    weight_dimension_note: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "product_id": self.product_id,
            "category": self.category,
            "score": self.score,
            "grade": self.grade,
            "violations": [
                {"field": v.field, "severity": v.severity, "message": v.message, "suggested_fix": v.suggested_fix}
                for v in self.violations
            ],
            "declared_fields": self.declared_fields,
            "actual_weight_grams": self.actual_weight_grams,
            "actual_dimensions_cm": self.actual_dimensions_cm,
            "weight_dimension_note": self.weight_dimension_note,
        }


_SEVERITY_WEIGHT = {"critical": 25, "major": 12, "minor": 5}

_GRADE_THRESHOLDS = [(95, "A+"), (85, "A"), (70, "B"), (50, "C"), (0, "D")]


def _grade_for_score(score: float) -> str:
    for threshold, grade in _GRADE_THRESHOLDS:
        if score >= threshold:
            return grade
    return "D"


# =========================================================================
# 5. OCR / GEMINI EXTRACTION (wrapped with retries)
# =========================================================================

@with_retries(max_attempts=3, retry_on=(TransientAPIError,))
def analyze_images_with_ocr(image_bytes_list: list[bytes], vision_client: Any) -> list[str]:
    """Run OCR over each label photo. Returns raw extracted text per image."""
    texts: list[str] = []
    for image_bytes in image_bytes_list:
        try:
            texts.append(vision_client.extract_text(image_bytes))
        except TransientAPIError:
            raise
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("OCR failed on one image, continuing with the rest: %s", exc)
            texts.append("")
    return texts


@with_retries(max_attempts=3, retry_on=(TransientAPIError,))
def analyze_product_data(ocr_texts: list[str], category: str, gemini_client: Any) -> dict[str, Any]:
    """Feed OCR text to Gemini to extract structured declared-label fields."""
    prompt = _build_extraction_prompt(ocr_texts, category)
    raw_response = gemini_client.generate(prompt)
    parsed = safe_json_loads(raw_response, default={})
    if not isinstance(parsed, dict):
        logger.warning("analyze_product_data: Gemini response was not a JSON object")
        return {}
    return parsed


def _build_extraction_prompt(ocr_texts: list[str], category: str) -> str:
    fields = required_fields_for_category(category)
    joined_text = "\n---\n".join(t for t in ocr_texts if t)
    field_list = ", ".join(fields)
    return (
        "Extract the following legal metrology fields from this product "
        f"label OCR text. Category: {category}. Fields to extract: {field_list}. "
        "Return ONLY a JSON object with those keys; omit a key entirely if the "
        f"label does not declare it.\n\nOCR TEXT:\n{joined_text}"
    )


# =========================================================================
# 6. SELLER-DECLARED ACTUAL VALUE VALIDATION
# =========================================================================

def validate_seller_declarations(
    declared_net_quantity_raw: Optional[str],
    actual_weight_raw: Optional[str],
    actual_dimensions_raw: Optional[str],
    tolerance_percent: float = 5.0,
) -> dict[str, Any]:
    """
    Compare the label's declared net quantity against the seller-typed actual
    weight. Degrades sensibly when a field is missing/unparseable.
    """
    result: dict[str, Any] = {
        "weight_match": None, "declared_grams": None, "actual_grams": None,
        "dimensions_actual_cm": None, "note": None,
    }

    declared_grams = normalize_weight_to_grams(declared_net_quantity_raw)
    actual_grams = normalize_weight_to_grams(actual_weight_raw)
    result["declared_grams"] = declared_grams
    result["actual_grams"] = actual_grams

    if declared_grams is None or actual_grams is None:
        result["note"] = "No manual measurement provided or declared net quantity unparseable — weight comparison skipped."
    else:
        allowed_diff = declared_grams * (tolerance_percent / 100.0)
        result["weight_match"] = abs(declared_grams - actual_grams) <= allowed_diff

    dims = normalize_dimensions_to_cm(actual_dimensions_raw)
    result["dimensions_actual_cm"] = dims
    if dims is None and actual_dimensions_raw:
        note = "Dimensions provided but could not be parsed — skipped."
        result["note"] = (result["note"] + " " if result["note"] else "") + note

    return result


# =========================================================================
# 7. SCORING + RECOMMENDATIONS (shared by both entry points)
# =========================================================================

def calculate_compliance_score(
    category: str,
    declared_fields: dict[str, Any],
    weight_dimension_validation: Optional[dict[str, Any]] = None,
) -> tuple[float, list[Violation]]:
    """Single source of truth for scoring, shared by both entry points."""
    violations: list[Violation] = []
    required = required_fields_for_category(category)

    for field_name in required:
        value = declared_fields.get(field_name)
        if value is None or (isinstance(value, str) and not value.strip()):
            severity = "critical" if field_name in ("mrp", "net_quantity", "manufacturer_name_address") else "major"
            label = FIELD_LABELS.get(field_name, field_name)
            violations.append(Violation(
                field=field_name, severity=severity,
                message=f"{label} is missing from the listing.",
                suggested_fix=f"Add {label.lower()} to the product label/description.",
            ))

    if weight_dimension_validation and weight_dimension_validation.get("weight_match") is False:
        declared_g = weight_dimension_validation["declared_grams"]
        actual_g = weight_dimension_validation["actual_grams"]
        violations.append(Violation(
            field="net_quantity", severity="critical",
            message=(f"Declared net quantity ({declared_g}g) does not match the "
                     f"seller-reported actual weight ({actual_g}g) within tolerance."),
            suggested_fix="Re-verify the package weight and correct the declared net quantity, or re-weigh the product.",
        ))

    score = 100.0
    for v in violations:
        score -= _SEVERITY_WEIGHT.get(v.severity, 5)
    score = max(0.0, round(score, 1))

    return score, violations


def generate_recommendations(violations: list[Violation]) -> list[str]:
    """Plain-language, ordered (critical first) fix list."""
    order = {"critical": 0, "major": 1, "minor": 2}
    ordered = sorted(violations, key=lambda v: order.get(v.severity, 3))
    return [v.suggested_fix for v in ordered]


# =========================================================================
# 8. THE TWO PUBLIC ENTRY POINTS (both share the core above)
# =========================================================================

def analyze_compliance(product_id: str, category: str, ocr_texts: list[str], gemini_client: Any) -> ComplianceResult:
    """Full pipeline entry point for a SCRAPED product."""
    if category not in VALID_CATEGORIES:
        logger.warning("Unknown category %r for product %s — falling back to 'general'", category, product_id)
        category = "general"

    declared_fields = analyze_product_data(ocr_texts, category, gemini_client)
    score, violations = calculate_compliance_score(category, declared_fields)

    return ComplianceResult(
        product_id=product_id, category=category, score=score,
        grade=_grade_for_score(score), violations=violations, declared_fields=declared_fields,
    )


def analyze_seller_upload_text(
    category: str,
    ocr_texts: list[str],
    gemini_client: Any,
    actual_weight: Optional[str] = None,
    actual_dimensions: Optional[str] = None,
) -> ComplianceResult:
    """
    Seller pre-upload self-check entry point. actual_weight and
    actual_dimensions are now HUMAN-TYPED STRINGS (where ESP32/load-cell/ToF
    sensor data used to land) — shares scoring with analyze_compliance().
    """
    if category not in VALID_CATEGORIES:
        logger.warning("Unknown category %r — falling back to 'general'", category)
        category = "general"

    declared_fields = analyze_product_data(ocr_texts, category, gemini_client)

    declared_net_quantity_raw = declared_fields.get("net_quantity")
    weight_dim_validation = validate_seller_declarations(
        declared_net_quantity_raw=declared_net_quantity_raw,
        actual_weight_raw=actual_weight,
        actual_dimensions_raw=actual_dimensions,
    )

    score, violations = calculate_compliance_score(category, declared_fields, weight_dim_validation)

    return ComplianceResult(
        product_id=None, category=category, score=score, grade=_grade_for_score(score),
        violations=violations, declared_fields=declared_fields,
        actual_weight_grams=weight_dim_validation.get("actual_grams"),
        actual_dimensions_cm=weight_dim_validation.get("dimensions_actual_cm"),
        weight_dimension_note=weight_dim_validation.get("note"),
    )


# =========================================================================
# 9. SAMPLE FIXTURE DATA (normally a separate JSON file — inlined here)
# =========================================================================

FIXTURES: dict[str, dict[str, Any]] = {
    "food_fully_compliant": {
        "category": "food",
        "declared_fields": {
            "mrp": "Rs. 250", "net_quantity": "500g",
            "manufacturer_name_address": "ABC Foods Pvt Ltd, Pune, Maharashtra",
            "country_of_origin": "India", "date_of_manufacture_or_packing": "01/2026",
            "consumer_care_details": "1800-123-4567", "batch_or_lot_number": "B12345",
            "best_before_or_expiry": "06/2026", "unit_sale_price": "Rs. 50/100g",
            "ingredients": "Wheat flour, sugar, salt", "fssai_number": "12345678901234",
        },
    },
    "electric_multiple_violations": {
        "category": "electric",
        "declared_fields": {"mrp": "Rs. 1999", "manufacturer_name_address": "", "country_of_origin": "China"},
    },
    "skincare_missing_image_partial_ocr": {
        "category": "skincare",
        "declared_fields": {"mrp": "Rs. 399", "net_quantity": "100ml", "country_of_origin": "India"},
    },
    "book_general_ok": {
        "category": "book",
        "declared_fields": {
            "mrp": "Rs. 499", "net_quantity": "1 unit",
            "manufacturer_name_address": "XYZ Publishers, Delhi",
            "country_of_origin": "India", "consumer_care_details": "support@xyzpublishers.com",
            "isbn": "978-3-16-148410-0",
        },
    },
}


def make_fake_gemini_client(declared_fields: dict):
    client = MagicMock()
    client.generate.return_value = "```json\n" + json.dumps(declared_fields) + "\n```"
    return client


# =========================================================================
# 10. TESTS (built-in unittest — no pip install needed)
# =========================================================================

class TestNormalizeWeight(unittest.TestCase):
    def test_grams_and_kg_variants(self):
        self.assertEqual(normalize_weight_to_grams("250g"), 250.0)
        self.assertEqual(normalize_weight_to_grams("0.25kg"), 250.0)
        self.assertEqual(normalize_weight_to_grams("1 KG"), 1000.0)
        self.assertEqual(normalize_weight_to_grams("  500 g  "), 500.0)
        self.assertEqual(normalize_weight_to_grams("2.5kg"), 2500.0)

    def test_blank_and_garbage_returns_none(self):
        self.assertIsNone(normalize_weight_to_grams(None))
        self.assertIsNone(normalize_weight_to_grams(""))
        self.assertIsNone(normalize_weight_to_grams("   "))
        self.assertIsNone(normalize_weight_to_grams("not measured"))
        self.assertIsNone(normalize_weight_to_grams("abc123xyz"))


class TestNormalizeDimensions(unittest.TestCase):
    def test_valid_formats(self):
        self.assertEqual(normalize_dimensions_to_cm("15x10x5cm"), (15.0, 10.0, 5.0))
        self.assertEqual(normalize_dimensions_to_cm("15 cm x 10 cm x 5cm"), (15.0, 10.0, 5.0))
        self.assertEqual(normalize_dimensions_to_cm("15CM X 10CM X 5CM"), (15.0, 10.0, 5.0))
        self.assertEqual(
            normalize_dimensions_to_cm("Length: 15cm, Width: 10cm, Height: 5cm"),
            (15.0, 10.0, 5.0),
        )

    def test_blank_and_garbage_returns_none(self):
        self.assertIsNone(normalize_dimensions_to_cm(None))
        self.assertIsNone(normalize_dimensions_to_cm(""))
        self.assertIsNone(normalize_dimensions_to_cm("not measured"))

    def test_mixed_units_uses_last_named_unit(self):
        self.assertEqual(normalize_dimensions_to_cm("15 x 10 x 5cm"), (15.0, 10.0, 5.0))


class TestJsonParsing(unittest.TestCase):
    def test_plain_fence(self):
        raw = '```json\n{"mrp": "100"}\n```'
        self.assertEqual(safe_json_loads(raw), {"mrp": "100"})

    def test_no_fence_with_prose(self):
        raw = 'Here is the extracted data: {"mrp": "100"} — let me know if you need more.'
        self.assertEqual(safe_json_loads(raw), {"mrp": "100"})

    def test_garbage_returns_default(self):
        self.assertEqual(safe_json_loads("not json at all", default={}), {})
        self.assertEqual(safe_json_loads(None, default={}), {})


class TestRetries(unittest.TestCase):
    def test_succeeds_after_transient_failures(self):
        calls = {"count": 0}

        @with_retries(max_attempts=3, base_delay_seconds=0)
        def flaky():
            calls["count"] += 1
            if calls["count"] < 3:
                raise TransientAPIError("rate limited")
            return "ok"

        self.assertEqual(flaky(), "ok")
        self.assertEqual(calls["count"], 3)

    def test_raises_after_exhausting_attempts(self):
        @with_retries(max_attempts=2, base_delay_seconds=0)
        def always_fails():
            raise TransientAPIError("still failing")

        with self.assertRaises(TransientAPIError):
            always_fails()


class TestScenarioNoViolations(unittest.TestCase):
    def test_fully_compliant_food_product(self):
        data = FIXTURES["food_fully_compliant"]
        gemini_client = make_fake_gemini_client(data["declared_fields"])

        result = analyze_compliance(
            product_id="P1001", category=data["category"],
            ocr_texts=["MRP Rs.250 Net Wt 500g ..."], gemini_client=gemini_client,
        )

        self.assertEqual(result.violations, [])
        self.assertEqual(result.score, 100.0)
        self.assertEqual(result.grade, "A+")


class TestScenarioMultipleViolations(unittest.TestCase):
    def test_electric_missing_several_fields(self):
        data = FIXTURES["electric_multiple_violations"]
        gemini_client = make_fake_gemini_client(data["declared_fields"])

        result = analyze_compliance(
            product_id="P1002", category=data["category"],
            ocr_texts=["Rs 1999 Made in China"], gemini_client=gemini_client,
        )

        violation_fields = {v.field for v in result.violations}
        self.assertIn("net_quantity", violation_fields)
        self.assertIn("manufacturer_name_address", violation_fields)
        self.assertIn("bis_certification", violation_fields)
        self.assertLess(result.score, 100.0)
        self.assertIn(result.grade, ("B", "C", "D"))


class TestScenarioMissingImage(unittest.TestCase):
    def test_ocr_handles_empty_image_list(self):
        vision_client = MagicMock()
        texts = analyze_images_with_ocr(image_bytes_list=[], vision_client=vision_client)
        self.assertEqual(texts, [])
        vision_client.extract_text.assert_not_called()

    def test_no_ocr_text_still_produces_a_report(self):
        gemini_client = make_fake_gemini_client({})
        result = analyze_compliance(
            product_id="P1003", category="general", ocr_texts=[], gemini_client=gemini_client,
        )
        self.assertLess(result.score, 100.0)
        self.assertGreater(len(result.violations), 0)
        self.assertIn(result.grade, ("A+", "A", "B", "C", "D"))


class TestScenarioBlurryLabel(unittest.TestCase):
    def test_ocr_survives_a_blurry_image(self):
        vision_client = MagicMock()

        def side_effect(image_bytes):
            if image_bytes == b"blurry":
                raise ValueError("could not decode image")
            return "clear label text"

        vision_client.extract_text.side_effect = side_effect

        texts = analyze_images_with_ocr(image_bytes_list=[b"clear", b"blurry"], vision_client=vision_client)
        self.assertEqual(texts, ["clear label text", ""])


class TestScenarioEmptyWeightDimensions(unittest.TestCase):
    def test_blank_weight_and_dimensions(self):
        data = FIXTURES["skincare_missing_image_partial_ocr"]
        gemini_client = make_fake_gemini_client(data["declared_fields"])

        result = analyze_seller_upload_text(
            category=data["category"], ocr_texts=["Rs 399 100ml Made in India"],
            gemini_client=gemini_client, actual_weight=None, actual_dimensions=None,
        )

        self.assertIsNone(result.actual_weight_grams)
        self.assertIsNone(result.actual_dimensions_cm)
        self.assertFalse(any(
            "does not match the seller-reported actual weight" in v.message
            for v in result.violations
        ))
        self.assertIn(result.grade, ("A+", "A", "B", "C", "D"))

    def test_messy_weight_input_that_matches(self):
        data = FIXTURES["food_fully_compliant"]
        gemini_client = make_fake_gemini_client(data["declared_fields"])

        result = analyze_seller_upload_text(
            category=data["category"], ocr_texts=["MRP Rs.250 Net Wt 500g"],
            gemini_client=gemini_client, actual_weight="0.5 kg", actual_dimensions="15 cm x 10 cm x 5cm",
        )

        self.assertEqual(result.actual_weight_grams, 500.0)
        self.assertEqual(result.actual_dimensions_cm, (15.0, 10.0, 5.0))
        self.assertFalse(any(v.field == "net_quantity" and "match" in v.message for v in result.violations))

    def test_real_weight_mismatch_is_flagged(self):
        data = FIXTURES["food_fully_compliant"]
        gemini_client = make_fake_gemini_client(data["declared_fields"])

        result = analyze_seller_upload_text(
            category=data["category"], ocr_texts=["MRP Rs.250 Net Wt 500g"],
            gemini_client=gemini_client, actual_weight="420g", actual_dimensions=None,
        )

        mismatch_violations = [v for v in result.violations if "does not match" in v.message]
        self.assertEqual(len(mismatch_violations), 1)
        self.assertEqual(mismatch_violations[0].severity, "critical")


class TestSharedScoringCore(unittest.TestCase):
    def test_both_entry_points_agree(self):
        data = FIXTURES["book_general_ok"]
        gemini_client_a = make_fake_gemini_client(data["declared_fields"])
        gemini_client_b = make_fake_gemini_client(data["declared_fields"])

        result_a = analyze_compliance(
            product_id="P2001", category=data["category"],
            ocr_texts=["some ocr text"], gemini_client=gemini_client_a,
        )
        result_b = analyze_seller_upload_text(
            category=data["category"], ocr_texts=["some ocr text"],
            gemini_client=gemini_client_b, actual_weight=None, actual_dimensions=None,
        )

        self.assertEqual(result_a.score, result_b.score)
        self.assertEqual(result_a.grade, result_b.grade)
        self.assertEqual(
            {v.field for v in result_a.violations},
            {v.field for v in result_b.violations},
        )


class TestUnknownCategory(unittest.TestCase):
    def test_falls_back_to_general(self):
        gemini_client = make_fake_gemini_client({"mrp": "100"})
        result = analyze_compliance(
            product_id="P3001", category="totally_unknown_category",
            ocr_texts=["x"], gemini_client=gemini_client,
        )
        self.assertEqual(result.category, "general")


class TestRecommendations(unittest.TestCase):
    def test_critical_ordered_first(self):
        violations = [
            Violation("x", "minor", "minor issue", "fix minor"),
            Violation("y", "critical", "critical issue", "fix critical"),
            Violation("z", "major", "major issue", "fix major"),
        ]
        recs = generate_recommendations(violations)
        self.assertEqual(recs, ["fix critical", "fix major", "fix minor"])


# =========================================================================
# RUN EVERYTHING WHEN THIS FILE IS EXECUTED DIRECTLY
# =========================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Running MetaMark compliance_engine.py test suite...")
    print("=" * 70)
    unittest.main(verbosity=2)