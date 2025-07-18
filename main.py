from fastapi import FastAPI, File, UploadFile, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pdf2image import convert_from_bytes
from docx import Document
import pytesseract
import os
import uuid
import traceback
import time

# 🔒 File upload configuration
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

app = FastAPI()

# ✅ CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://convertingtools.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🧾 Optional info route for frontend to fetch limits
@app.get("/info")
def get_info():
    return {
        "max_file_size_mb": MAX_FILE_SIZE_MB,
        "allowed_types": ["application/pdf"]
    }

# 🧹 Safe file cleanup with delay
def delayed_delete(path: str):
    time.sleep(10)
    if os.path.exists(path):
        os.remove(path)

@app.post("/convert-ocr")
async def convert_ocr(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    try:
        contents = await file.read()

        # ✅ File size check
        if len(contents) > MAX_FILE_SIZE_BYTES:
            return JSONResponse(
                content={"error": f"File too large. Max allowed size is {MAX_FILE_SIZE_MB} MB."},
                status_code=413
            )

        # ✅ File type check
        if not file.filename.lower().endswith(".pdf") or file.content_type != "application/pdf":
            return JSONResponse(
                content={"error": "Invalid file. Only PDF files are accepted."},
                status_code=400
            )

        # ✅ OCR Conversion
        images = convert_from_bytes(contents)
        extracted_text = "\n".join(pytesseract.image_to_string(img) for img in images)

        doc = Document()
        for line in extracted_text.splitlines():
            doc.add_paragraph(line)

        output_filename = f"{uuid.uuid4()}.docx"
        doc.save(output_filename)

        # ✅ Delayed cleanup
        background_tasks.add_task(delayed_delete, output_filename)

        # ✅ Return file with safe CORS header
        response = FileResponse(
            path=output_filename,
            filename="converted.docx",
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response

    except Exception as e:
        print("🔥 ERROR:", traceback.format_exc())
        return JSONResponse(
            content={"error": "Internal server error", "details": str(e)},
            status_code=500
        )
