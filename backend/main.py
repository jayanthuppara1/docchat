from fastapi import FastAPI
from fastapi import UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from anthropic import Anthropic
from dotenv import load_dotenv
from pydantic import BaseModel
import fitz  # PyMuPDF's import name
import uuid
import os

load_dotenv()
client = Anthropic()

app = FastAPI(title="DocChat API")

sessions = {}
UPLOAD_DIR = "uploads"
MAX_UPLOAD_SIZE = 10 * 1024 * 1024

os.makedirs(UPLOAD_DIR, exist_ok=True)


class ChatRequest(BaseModel):
    session_id: str
    message: str

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

    prompt = f"""You are reviewing a document for someone who needs to understand it before signing or agreeing to it.

Document content:
{document_text}

Provide:
1. A simple summary of what this document is and its main purpose
2. Key terms, obligations, fees, deadlines, or responsibilities
3. Any clauses that may need careful review (penalties, cancellation terms, auto-renewal, liability, deposits)

End with: "This summary is for understanding only and is not legal advice."
"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="Could not generate summary. Please try again."
        ) from exc

    summary_text = response.content[0].text

    return {"summary": summary_text}


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
