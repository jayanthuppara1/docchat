const API_URL = window.location.port === "5500" ? "http://127.0.0.1:8000" : "";

let sessionId = null;

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function toArray(value) {
  if (Array.isArray(value)) return value;
  if (value === undefined || value === null || value === "") return [];
  return [String(value)];
}

document.getElementById("uploadBtn").addEventListener("click", async () => {
  const fileInput = document.getElementById("fileInput");
  const file = fileInput.files[0];

  if (!file) {
    alert("Please choose a PDF file first");
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  document.getElementById("status").textContent = "Uploading and processing...";

  const response = await fetch(`${API_URL}/upload`, {
    method: "POST",
    body: formData
  });

  if (!response.ok) {
    const error = await response.json();
    document.getElementById("status").textContent = "Error: " + error.detail;
    return;
  }

  const data = await response.json();
  sessionId = data.session_id;

  document.getElementById("status").textContent =
    `Uploaded: ${data.filename} (${data.page_count} pages)`;

  document.getElementById("summaryBtn").disabled = false;
  document.getElementById("chatInput").disabled = false;
  document.getElementById("sendBtn").disabled = false;
});

document.getElementById("summaryBtn").addEventListener("click", async () => {
  const summaryEl = document.getElementById("summary");
  const summaryBtn = document.getElementById("summaryBtn");
  summaryEl.innerHTML = "Generating summary...";
  summaryBtn.disabled = true;

  try {
    const response = await fetch(`${API_URL}/summary?session_id=${sessionId}`, {
      method: "POST"
    });

    if (!response.ok) {
      const error = await response.json();
      summaryEl.innerHTML = "Error: " + escapeHtml(error.detail || "Could not generate summary");
      return;
    }

    const data = await response.json();
    const keyTerms = toArray(data.key_terms);
    const risks = toArray(data.risks);
    const overview = data.overview || "No overview was returned.";
    const disclaimer = data.disclaimer || "This summary is for understanding only and is not legal advice.";

    let html = `<h3>Overview</h3><p>${escapeHtml(overview)}</p>`;

    if (keyTerms.length > 0) {
      html += `<h3>Key Terms</h3><ul>`;
      keyTerms.forEach(item => html += `<li>${escapeHtml(item)}</li>`);
      html += `</ul>`;
    }

    if (risks.length > 0) {
      html += `<h3>⚠️ Risks to Review</h3><ul>`;
      risks.forEach(item => html += `<li class="risk">${escapeHtml(item)}</li>`);
      html += `</ul>`;
    }

    html += `<p class="disclaimer">${escapeHtml(disclaimer)}</p>`;

    summaryEl.innerHTML = html;
  } catch (error) {
    summaryEl.innerHTML = "Error: Could not display the summary. Please try again.";
  } finally {
    summaryBtn.disabled = false;
  }
});

document.getElementById("sendBtn").addEventListener("click", async () => {
  const input = document.getElementById("chatInput");
  const message = input.value.trim();
  if (!message) return;

  const chatDiv = document.getElementById("chat");
  chatDiv.innerHTML += `<p class="msg-user"><b>You:</b> ${escapeHtml(message)}</p>`;
  input.value = "";

  const response = await fetch(`${API_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, message: message })
  });

  if (!response.ok) {
    const error = await response.json();
    chatDiv.innerHTML += `<p>Error: ${error.detail}</p>`;
    return;
  }

  const data = await response.json();
  chatDiv.innerHTML += `<p class="msg-assistant"><b>DocChat:</b> ${data.answer}</p>`;
  chatDiv.scrollTop = chatDiv.scrollHeight;
});
