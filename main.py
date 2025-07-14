from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from pdf2image import convert_from_bytes
import pytesseract
from io import BytesIO
import os
from pdf2docx import Converter
import uuid

app = FastAPI()

@app.post("/convert-ocr")
async def convert_ocr(file: UploadFile = File(...)):
    contents = await file.read()
    images = convert_from_bytes(contents)
    text = "\n".join(pytesseract.image_to_string(img) for img in images)
    return {"text": text}

    # 2. Generate output file path
    output_filename = input_filename.replace(".pdf", ".docx")

    # 3. Convert PDF to DOCX
    cv = Converter(input_filename)
    cv.convert(output_filename, start=0, end=None)
    cv.close()

    # 4. Return DOCX as streaming response
    response = StreamingResponse(
        open(output_filename, "rb"),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename=converted.docx"},
    )

    # 5. Cleanup after sending
    @response.call_on_close
    def cleanup():
        os.remove(input_filename)
        os.remove(output_filename)

    return response
