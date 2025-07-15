from fastapi import FastAPI, File, UploadFile, BackgroundTasks
from fastapi.responses import StreamingResponse
from pdf2image import convert_from_bytes
from docx import Document
import pytesseract
from io import BytesIO
import os
import uuid

app = FastAPI()

@app.post("/convert-ocr")
async def convert_ocr(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    contents = await file.read()

    # 1. Convert PDF to images
    images = convert_from_bytes(contents)

    # 2. OCR each image
    extracted_text = "\n".join(pytesseract.image_to_string(img) for img in images)

    # 3. Create DOCX
    doc = Document()
    for line in extracted_text.splitlines():
        doc.add_paragraph(line)

    # 4. Save DOCX to temp file
    output_filename = f"{uuid.uuid4()}.docx"
    doc.save(output_filename)

    # 5. Register file cleanup in background
    background_tasks.add_task(os.remove, output_filename)

    # 6. Stream DOCX
    return StreamingResponse(
        open(output_filename, "rb"),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": "attachment; filename=converted.docx"}
    )
