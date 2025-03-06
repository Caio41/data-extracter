from io import BytesIO, StringIO
from pathlib import Path
from fastapi import APIRouter, File, UploadFile
from fastapi.responses import StreamingResponse
from docx import Document
from pdf2image import convert_from_bytes
import pytesseract
from PIL import Image

from services.text_correction import corrigir_texto


router = APIRouter()


@router.post("/img-to-doc")
async def img_to_doc(arquivo: UploadFile = File(...)):
    """Cria documento Word com texto da imagem"""
    file_content = await arquivo.read()
    
    # transformamos em img pra o pytesseract conseguir ler
    img = Image.open(BytesIO(file_content))
    txt_extraido = pytesseract.image_to_string(img, lang='por')

    doc = Document()
    doc.add_paragraph(txt_extraido)

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


@router.post("/img-to-txt")
async def img_to_txt(arquivo: UploadFile = File(...)):
    """Cria documento txt com texto da imagem"""
    file_content = await arquivo.read()

    img = Image.open(BytesIO(file_content))
    txt_extraido = pytesseract.image_to_string(img, lang='por')

    nome_doc = Path(arquivo.filename).stem

    output = StringIO(txt_extraido)

    return StreamingResponse(
        output,
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename={nome_doc}.txt"},
    )


@router.post("/img-to-doc-pdf")
async def img_to_doc_pdf(arquivo: UploadFile = File(...)):
    """Cria documento Word com texto da imagem"""
    file_content = await arquivo.read()
    
    pages = convert_from_bytes(file_content, 300)
    txt_completo = ''
    for page in pages:
        txt = pytesseract.image_to_string(page, lang='por')
        txt_completo += txt + '\n'

    doc = Document()
    doc.add_paragraph(txt_completo)

    output = BytesIO()
    doc.save(output)
    output.seek(0)

    nome_doc = Path(arquivo.filename).stem

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename={nome_doc}.docx"},
    )




@router.post("/img-to-txt-pdf")
async def img_to_txt_pdf(arquivo: UploadFile = File(...)):
    """Cria documento txt com texto da imagem"""
    file_content = await arquivo.read()

    pages = convert_from_bytes(file_content, 300)
    txt_completo = ''
    for page in pages:
        txt = pytesseract.image_to_string(page, lang='por')
        txt_completo += txt + '\n'

    nome_doc = Path(arquivo.filename).stem

    output = StringIO(txt_completo)

    return StreamingResponse(
        output,
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename={nome_doc}.txt"},
    )