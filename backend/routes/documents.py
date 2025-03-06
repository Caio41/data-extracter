from io import BytesIO, StringIO
from pathlib import Path
from fastapi import APIRouter, File, UploadFile
from fastapi.responses import StreamingResponse
from docx import Document
import fitz
import ocrmypdf
from ocrmypdf.exceptions import TaggedPDFError
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



# pra rodar essas de pdf precisa do poppler baixado por causa do pdf2image
# download windows: https://github.com/oschwartz10612/poppler-windows/releases/tag/v24.08.0-0

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
    # Não vai funcionar bem para PDFs híbridos (com texto e imagens)

    # Se o texto não é selecionável (PDF de Imagem)
    try:
        input_pdf = BytesIO(file_content)  
        output = BytesIO()

        # É possível usar o argumento skip_text=True aqui pra poder pular as páginas que tem texto,
        # mas nao funciona pros PDFs hibridos pq pode ter uma pagina que tem tanto texto quanto imagem
        ocrmypdf.ocr(input_pdf, output, language='por') 

        output.seek(0)

        doc = fitz.open(stream=output, filetype='pdf')

    # Se o texto é selecionavel (PDF de Texto)
    except TaggedPDFError:
        doc = fitz.open(stream=file_content, filetype='pdf')
        
    txt_completo = ''
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        txt_completo += page.get_text()

    nome_doc = Path(arquivo.filename).stem

    output = StringIO(txt_completo)

    return StreamingResponse(
        output,
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename={nome_doc}.txt"},
    )