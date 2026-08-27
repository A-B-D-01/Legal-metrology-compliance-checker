const DEFAULT_API_URL = "http://127.0.0.1:5000";

const apiUrlInput = document.getElementById("apiUrl");
const saveButton = document.getElementById("save");
const statusElement = document.getElementById("status");

async function loadSettings() {
  const stored = await chrome.storage.local.get(["apiUrl"]);
  apiUrlInput.value = stored.apiUrl || DEFAULT_API_URL;
}

async function saveSettings() {
  const apiUrl = apiUrlInput.value.trim().replace(/\/+$/, "");

  if (!/^https?:\/\/[^/\s]+(?::\d+)?$/i.test(apiUrl)) {
    statusElement.textContent = "Enter a valid backend URL.";
    return;
  }

  await chrome.storage.local.set({ apiUrl });
  statusElement.textContent = "Settings saved.";
}

saveButton.addEventListener("click", saveSettings);

loadSettings();
