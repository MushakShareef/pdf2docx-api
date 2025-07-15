from fastapi import FastAPI, File, UploadFile, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pdf2image import convert_from_bytes
from docx import Document
import pytesseract
from io import BytesIO
import os
import uuid
import traceback

app = FastAPI()

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://convertingtools.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/convert-ocr")
async def convert_ocr(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    try:
        contents = await file.read()
        images = convert_from_bytes(contents)
        extracted_text = "\n".join(pytesseract.image_to_string(img) for img in images)

        doc = Document()
        for line in extracted_text.splitlines():
            doc.add_paragraph(line)

        output_filename = f"{uuid.uuid4()}.docx"
        doc.save(output_filename)

        background_tasks.add_task(os.remove, output_filename)

        return StreamingResponse(
            open(output_filename, "rb"),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": "attachment; filename=converted.docx"}
        )

    except Exception as e:
        print("🔥 ERROR:", traceback.format_exc())  # This will print error in Render logs
        return {"error": "Internal server error", "details": str(e)}
