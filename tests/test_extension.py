import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXTENSION = ROOT / "extension"


def test_extension_files_exist():
    expected_files = {
        "manifest.json",
        "popup.html",
        "popup.js",
        "options.html",
        "options.js",
    }

    actual_files = {
        path.name
        for path in EXTENSION.iterdir()
        if path.is_file()
    }

    assert expected_files.issubset(actual_files)


def test_manifest_is_manifest_v3():
    manifest = json.loads(
        (EXTENSION / "manifest.json").read_text(encoding="utf-8")
    )

    assert manifest["manifest_version"] == 3
    assert manifest["name"] == "LegalGuard Compliance Checker"
    assert manifest["action"]["default_popup"] == "popup.html"


def test_manifest_has_required_permissions():
    manifest = json.loads(
        (EXTENSION / "manifest.json").read_text(encoding="utf-8")
    )

    assert "activeTab" in manifest["permissions"]
    assert "storage" in manifest["permissions"]


def test_manifest_allows_legalguard_backend():
    manifest = json.loads(
        (EXTENSION / "manifest.json").read_text(encoding="utf-8")
    )

    hosts = manifest["host_permissions"]

    assert "http://localhost:5000/*" in hosts
    assert "http://127.0.0.1:5000/*" in hosts


def test_popup_calls_scrape_endpoint():
    popup = (EXTENSION / "popup.js").read_text(encoding="utf-8")

    assert "/api/scrape" in popup
    assert 'method: "POST"' in popup
    assert '"Content-Type": "application/json"' in popup


def test_popup_sends_current_page_url():
    popup = (EXTENSION / "popup.js").read_text(encoding="utf-8")

    assert "chrome.tabs.query" in popup
    assert "body: JSON.stringify" in popup
    assert "url: tab.url" in popup


def test_extension_supports_configurable_api_url():
    popup = (EXTENSION / "popup.js").read_text(encoding="utf-8")
    options = (EXTENSION / "options.js").read_text(encoding="utf-8")

    assert "chrome.storage.local" in popup
    assert "chrome.storage.local" in options
    assert "apiUrl" in popup
    assert "apiUrl" in options


def test_extension_rejects_non_http_urls():
    popup = (EXTENSION / "popup.js").read_text(encoding="utf-8")

    assert r"/^https?:\/\//i.test(tab.url)" in popup


def test_extension_contains_no_hardware_dependencies():
    prohibited_patterns = (
        r"\barduino\b",
        r"\besp32\b",
        r"\braspberry\s+pi\b",
        r"\bgpio\b",
        r"\bbluetooth\b",
        r"\bble\b",
        r"\bsensor\b",
        r"\bserial\b",
    )

    extension_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in EXTENSION.rglob("*")
        if path.is_file() and path.suffix in {".js", ".html", ".json"}
    ).lower()

    for pattern in prohibited_patterns:
        assert re.search(pattern, extension_text) is None
