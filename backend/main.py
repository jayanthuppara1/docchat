from fastapi import FastAPI
from fastapi import UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import fitz  # PyMuPDF's import name
import uuid
import os

app = FastAPI(title="DocChat API")

sessions = {}

os.makedirs("uploads", exist_ok=True)

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
