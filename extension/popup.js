const DEFAULT_API_URL = "http://127.0.0.1:5000";

const checkButton = document.getElementById("checkButton");
const statusElement = document.getElementById("status");
const resultElement = document.getElementById("result");

function setStatus(message) {
  statusElement.textContent = message;
}

function setResult(result) {
  resultElement.textContent = result;
}

async function getApiUrl() {
  const stored = await chrome.storage.local.get(["apiUrl"]);
  return stored.apiUrl || DEFAULT_API_URL;
}

async function getCurrentTab() {
  const tabs = await chrome.tabs.query({
    active: true,
    currentWindow: true
  });

  if (!tabs.length || !tabs[0].url) {
    throw new Error("Unable to determine the current page URL.");
  }

  return tabs[0];
}

async function checkCompliance() {
  checkButton.disabled = true;
  setStatus("Checking...");
  setResult("");

  try {
    const tab = await getCurrentTab();

    if (!/^https?:\/\//i.test(tab.url)) {
      throw new Error("The current page must use HTTP or HTTPS.");
    }

    const apiUrl = await getApiUrl();

    const response = await fetch(`${apiUrl}/api/scrape`, {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        url: tab.url
      })
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        data.message || data.error || `Request failed with status ${response.status}.`
      );
    }

    const result = data.data || data;

    setStatus("Scrape successful.");

    setResult(
      `URL: ${result.url || tab.url}\n` +
      `Title: ${result.title || "N/A"}\n` +
      `Page length: ${result.page_length ?? "N/A"}\n` +
      `Load time: ${result.load_time_seconds ?? "N/A"} seconds`
    );
  } catch (error) {
    setStatus("Check failed.");
    setResult(error.message || "Unexpected error.");
  } finally {
    checkButton.disabled = false;
  }
}

checkButton.addEventListener("click", checkCompliance);
