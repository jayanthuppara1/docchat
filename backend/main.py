from fastapi import FastAPI
from fastapi import UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from anthropic import Anthropic
from dotenv import load_dotenv
from pydantic import BaseModel
import fitz  # PyMuPDF's import name
import uuid
import os
import json

load_dotenv()
client = Anthropic()

app = FastAPI(title="DocChat API")

sessions = {}
UPLOAD_DIR = "uploads"
MAX_UPLOAD_SIZE = 10 * 1024 * 1024
SUMMARY_MAX_INPUT_CHARS = 60000
SUMMARY_DISCLAIMER = "This summary is for understanding only and is not legal advice."
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

os.makedirs(UPLOAD_DIR, exist_ok=True)


class ChatRequest(BaseModel):
    session_id: str
    message: str


def parse_summary_response(raw: str):
    cleaned = raw.strip()

    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()

    if not cleaned.startswith("{") and '"overview"' in cleaned:
        cleaned = "{" + cleaned

    try:
        summary_data = json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        if start == -1:
            raise
        summary_data, _ = json.JSONDecoder().raw_decode(cleaned[start:])

    if not isinstance(summary_data, dict):
        raise ValueError("Summary response must be a JSON object")

    for key in ("overview", "key_terms", "risks", "disclaimer"):
        if key not in summary_data:
            raise ValueError(f"Missing summary field: {key}")

    if not isinstance(summary_data["overview"], str):
        raise ValueError("Summary overview must be a string")
    if not isinstance(summary_data["key_terms"], list):
        raise ValueError("Summary key_terms must be a list")
    if not isinstance(summary_data["risks"], list):
        raise ValueError("Summary risks must be a list")
    if not isinstance(summary_data["disclaimer"], str):
        raise ValueError("Summary disclaimer must be a string")

    summary_data["key_terms"] = [str(item) for item in summary_data["key_terms"]]
    summary_data["risks"] = [str(item) for item in summary_data["risks"]]

    return summary_data


def fallback_summary_response(raw: str):
    fallback_text = raw.strip()
    if not fallback_text:
        fallback_text = "A summary was generated, but it could not be displayed in the expected format."

    return {
        "overview": fallback_text,
        "key_terms": [],
        "risks": [
            "The response could not be fully structured, so review the original document for exact terms."
        ],
        "disclaimer": SUMMARY_DISCLAIMER
    }

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    content = await file.read()
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail="PDF must be 10MB or smaller")

    session_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{session_id}.pdf")
    with open(file_path, "wb") as f:
        f.write(content)

    try:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        page_count = len(doc)
        doc.close()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Could not process this PDF") from exc

    if not text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from this PDF")

    sessions[session_id] = {
        "filename": file.filename,
        "text": text,
        "chat_history": []
    }

    return {
        "session_id": session_id,
        "filename": file.filename,
        "page_count": page_count
    }


@app.post("/summary")
async def get_summary(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    document_text = sessions[session_id]["text"]
    summary_context = document_text[:SUMMARY_MAX_INPUT_CHARS]
    if len(document_text) > SUMMARY_MAX_INPUT_CHARS:
        summary_context += (
            "\n\n[Document text was shortened for this v1 summary because it is long. "
            "Summarize only the provided extracted text and avoid inventing missing details.]"
        )

    prompt = f"""You are reviewing a document for someone who needs to understand it before signing or agreeing to it.

Document content:
{summary_context}

Respond with ONLY compact, valid JSON. Do not include markdown, code fences, explanations, or trailing commas.

Use this exact structure:

{{
  "overview": "1-2 sentence plain-language summary of what this document is",
  "key_terms": ["term 1: explanation", "term 2: explanation"],
  "risks": ["risk 1: why it matters", "risk 2: why it matters"],
  "disclaimer": "{SUMMARY_DISCLAIMER}"
}}

Rules:
- Return at most 8 key_terms.
- Return at most 6 risks.
- Keep each list item under 25 words.
- If there are no notable risks, return an empty array for risks.
- Start with "overview" and end with the closing JSON brace.
"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}]
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="Could not generate summary. Please try again."
        ) from exc

    raw = response.content[0].text

    try:
        summary_data = parse_summary_response(raw)
    except (json.JSONDecodeError, ValueError, TypeError) as exc:
        summary_data = fallback_summary_response(raw)

    return summary_data


@app.post("/chat")
async def chat(request: ChatRequest):
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    message = request.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    session = sessions[request.session_id]
    document_text = session["text"]

    context_prompt = f"""You are answering questions about a document for someone reviewing it before signing or agreeing to it.

Document content:
{document_text}

Answer the user's question based only on this document. If the answer is not in the document, say so clearly. Keep the answer simple and avoid legal advice -- if relevant, add a brief disclaimer.

User's question: {message}
"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[{"role": "user", "content": context_prompt}]
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="Could not generate an answer. Please try again."
        ) from exc

    answer = response.content[0].text

    session["chat_history"].append({"role": "user", "content": message})
    session["chat_history"].append({"role": "assistant", "content": answer})

    return {"answer": answer}


app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
