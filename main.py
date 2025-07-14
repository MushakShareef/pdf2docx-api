from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
from pdf2docx import Converter
import os
import uuid

app = FastAPI()

@app.post("/convert")
async def convert_pdf_to_docx(file: UploadFile = File(...)):
    # 1. Save uploaded PDF to a temp file
    input_filename = f"temp_{uuid.uuid4().hex}.pdf"
    with open(input_filename, "wb") as f:
        f.write(await file.read())

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
