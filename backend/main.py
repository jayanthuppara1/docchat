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

os.makedirs("uploads", exist_ok=True)


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
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    page_count = len(doc)
    doc.close()

    if not text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from this PDF")

    session_id = str(uuid.uuid4())
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

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )

    summary_text = response.content[0].text

    return {"summary": summary_text}


@app.post("/chat")
async def chat(request: ChatRequest):
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = sessions[request.session_id]
    document_text = session["text"]

    context_prompt = f"""You are answering questions about a document for someone reviewing it before signing or agreeing to it.

Document content:
{document_text}

Answer the user's question based only on this document. If the answer is not in the document, say so clearly. Keep the answer simple and avoid legal advice -- if relevant, add a brief disclaimer.

User's question: {request.message}
"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": context_prompt}]
    )

    answer = response.content[0].text

    session["chat_history"].append({"role": "user", "content": request.message})
    session["chat_history"].append({"role": "assistant", "content": answer})

    return {"answer": answer}
