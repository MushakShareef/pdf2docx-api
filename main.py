from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
from pdf2image import convert_from_bytes
from docx import Document
import pytesseract
from io import BytesIO
import os
import uuid

app = FastAPI()

@app.post("/convert-ocr")
async def convert_ocr(file: UploadFile = File(...)):
    contents = await file.read()

    # 1. Convert PDF pages to images
    images = convert_from_bytes(contents)

    # 2. Use OCR to extract text from each image
    extracted_text = "\n".join(pytesseract.image_to_string(img) for img in images)

    # 3. Create Word document
    doc = Document()
    for line in extracted_text.splitlines():
        doc.add_paragraph(line)

    # 4. Save to a temporary DOCX file
    output_filename = f"{uuid.uuid4()}.docx"
    doc.save(output_filename)

    # 5. Stream the file as response
    def cleanup():
        try:
            os.remove(output_filename)
        except:
            pass

    return StreamingResponse(
        open(output_filename, "rb"),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": "attachment; filename=converted.docx"},
        background=cleanup
    )
