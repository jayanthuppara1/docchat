const API_URL = "http://127.0.0.1:8000";

let sessionId = null;

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
