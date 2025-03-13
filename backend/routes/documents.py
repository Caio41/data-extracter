from io import BytesIO, StringIO
from pathlib import Path
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from docx import Document
import pytesseract
from PIL import Image

from services.pdf_utils import ocr_pdf
from services.text_correction import corrigir_texto


router = APIRouter()


@router.post("/img-to-doc")
async def img_to_doc(arquivo: UploadFile = File(...)) -> StreamingResponse:
    """Cria documento Word com texto da imagem"""
    file_content = await arquivo.read()
    
    # Aplicação do OCR
    if arquivo.content_type == 'application/pdf':
        txt_extraido = ocr_pdf(file_content)
    else:
        img = Image.open(BytesIO(file_content))
        txt_extraido = pytesseract.image_to_string(img, lang='por')


    if not txt_extraido:
        raise HTTPException(status_code=400, detail='Não foi possível detectar nenhum texto na imagem.')

    txt_corrigido = corrigir_texto(txt_extraido)

    # Criação do doc
    doc = Document()
    doc.add_paragraph(txt_corrigido)

    output = BytesIO()
    doc.save(output)
    output.seek(0)

    # Pega nome do arquivo sem extensão
    nome_doc = Path(arquivo.filename).stem

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename={nome_doc}.docx"},
    )


@router.post("/img-to-txt")
async def img_to_txt(arquivo: UploadFile = File(...)) -> StreamingResponse:
    """Cria documento txt com texto da imagem"""
    file_content = await arquivo.read()

    # Aplicação do OCR
    if arquivo.content_type == 'application/pdf':
        txt_extraido = ocr_pdf(file_content)
    else:
        img = Image.open(BytesIO(file_content))
        txt_extraido = pytesseract.image_to_string(img, lang='por')

    if not txt_extraido:
        raise HTTPException(status_code=400, detail='Não foi possível detectar nenhum texto na imagem.')

    txt_corrigido = corrigir_texto(txt_extraido)

    # Criação do txt
    nome_doc = Path(arquivo.filename).stem

    output = StringIO(txt_corrigido)

    return StreamingResponse(
        output,
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename={nome_doc}.txt"},
    )
