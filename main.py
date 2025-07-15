from fastapi import FastAPI, File, UploadFile, BackgroundTasks
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pdf2image import convert_from_bytes
from docx import Document
import pytesseract
from io import BytesIO
import os
import uuid

app = FastAPI()

# ✅ CORS middleware - VERY IMPORTANT
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://convertingtools.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/convert-ocr")
async def convert_ocr(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    contents = await file.read()
    images = convert_from_bytes(contents)
    text = "\n".join(pytesseract.image_to_string(img) for img in images)

    doc = Document()
    for line in text.splitlines():
        doc.add_paragraph(line)

    filename = f"{uuid.uuid4()}.docx"
    doc.save(filename)

    background_tasks.add_task(os.remove, filename)

    return StreamingResponse(
        open(filename, "rb"),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": "attachment; filename=converted.docx"}
    )
