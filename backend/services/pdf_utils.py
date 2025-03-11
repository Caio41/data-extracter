from io import BytesIO

import fitz
import ocrmypdf
from ocrmypdf.exceptions import TaggedPDFError


def ocr_pdf(file_content: bytes) -> str:
    """Realiza OCR em PDFs"""
    try:
        input_pdf = BytesIO(file_content)
        output = BytesIO()

        ocrmypdf.ocr(input_pdf, output, language="por", skip_text=True)

        output.seek(0)

        doc = fitz.open(stream=output, filetype="pdf")

    # Se o texto é selecionavel (PDF de Texto)
    except TaggedPDFError:
        doc = fitz.open(stream=file_content, filetype="pdf")

    txt_completo = ""
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        txt_completo += page.get_text()

    return txt_completo
