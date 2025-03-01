from io import BytesIO
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from fastapi import APIRouter, File, UploadFile
from fastapi.responses import StreamingResponse
import numpy as np
import easyocr
import pytesseract
import fitz
from PIL import Image
import cv2
import ocrmypdf
from docx import Document


router = APIRouter()

reader = easyocr.Reader(["pt", "en"])


# easyocr puro, so funciona pra imagens (png, jpg, etc)
@router.post("/easyocr-png")
def teste(arquivo: UploadFile = File(...)):
    with NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(arquivo.file.read())
        temp_file_path = temp_file.name

    result = reader.readtext(temp_file_path, detail=0)

    os.remove(temp_file_path)
    return result


@router.post("/img-to-doc")
async def img_to_doc(arquivo: UploadFile = File(...)):
    """Cria documento Word com texto da imagem"""
    file_content = await arquivo.read()
    result = reader.readtext(file_content, paragraph=True, detail=0)

    doc = Document()
    for text in result:
        doc.add_paragraph(text)

    output = BytesIO()
    doc.save(output)
    output.seek(0)

    # pega nome do arquivo sem extensão
    nome_doc = Path(arquivo.filename).stem

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename={nome_doc}.docx"},
    )


# usa ocrmypdf e fitz
@router.post("/easyocr-pdf")
async def easyocr_pdf(arquivo: UploadFile = File(...)):
    file_content = await arquivo.read()

    output = BytesIO()

    with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(file_content)
        tmp_file_path = tmp_file.name

    ocrmypdf.ocr(tmp_file_path, output, language="por")

    output.seek(0)
    output_content = output.read()
    doc = fitz.open(stream=output_content)
    texto_extraido = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        texto_extraido += page.get_text("text")

    print(texto_extraido)
    return texto_extraido


# tesseract com fitz pra tentar ler pdf
@router.post("/tesseract")
async def tesseract_teste(arquivo: UploadFile = File(...)):
    file_content = await arquivo.read()

    doc = fitz.open(stream=file_content, filetype="pdf")

    texto_extraido = ""
    for page in doc:
        pix = page.get_pixmap()
        img = Image.open(BytesIO(pix.tobytes("png")))
        # img = preprocessar_imagem(img)
        text = pytesseract.image_to_string(img, lang="por")
        texto_extraido += text + "\n"

    print(texto_extraido)
    return texto_extraido


def preprocessar_imagem(img):
    img_cv = np.array(img)
    img_cv = cv2.cvtColor(img_cv, cv2.COLOR_RGB2GRAY)

    img_cv = cv2.adaptiveThreshold(
        img_cv, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )

    return Image.fromarray(img_cv)
