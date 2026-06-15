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
  document.getElementById("summary").innerHTML = "Generating summary...";

  const response = await fetch(`${API_URL}/summary?session_id=${sessionId}`, {
    method: "POST"
  });

  if (!response.ok) {
    const error = await response.json();
    document.getElementById("summary").innerHTML = "Error: " + escapeHtml(error.detail);
    return;
  }

  const data = await response.json();

  let html = `<h3>Overview</h3><p>${escapeHtml(data.overview)}</p>`;

  html += `<h3>Key Terms</h3><ul>`;
  data.key_terms.forEach(item => html += `<li>${escapeHtml(item)}</li>`);
  html += `</ul>`;

  if (data.risks.length > 0) {
    html += `<h3>⚠️ Risks to Review</h3><ul>`;
    data.risks.forEach(item => html += `<li class="risk">${escapeHtml(item)}</li>`);
    html += `</ul>`;
  }

  html += `<p class="disclaimer">${escapeHtml(data.disclaimer)}</p>`;

  document.getElementById("summary").innerHTML = html;
});

document.getElementById("sendBtn").addEventListener("click", async () => {
  const input = document.getElementById("chatInput");
  const message = input.value.trim();
  if (!message) return;

  const chatDiv = document.getElementById("chat");
  chatDiv.innerHTML += `<p class="msg-user"><b>You:</b> ${message}</p>`;
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
