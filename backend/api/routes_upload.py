import os
import uuid
from fastapi import APIRouter, UploadFile, File
from backend.rag.loader import PDFLoader
from backend.rag.splitter import TextSplitter
from backend.rag.embeddings import embed
from backend.rag.vector_store import vector_store

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...)
):

    file_id = str(uuid.uuid4())[:8]
    path = os.path.join(
        UPLOAD_DIR,
        f"{file_id}_{file.filename}"
    )

    with open(path, "wb") as f:
        f.write(
            await file.read()
        )

    loader = PDFLoader()
    text = loader.load(path)

    splitter = TextSplitter()
    chunks = splitter.split(text)

    vectors = embed(chunks)

    vector_store.add(
        vectors,
        chunks
    )

    return {
        "filename": file.filename,
        "chunks": len(chunks),
        "chars": len(text)
    }
