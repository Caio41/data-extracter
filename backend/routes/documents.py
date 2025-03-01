from io import BytesIO, StringIO
from pathlib import Path
import easyocr
from fastapi import APIRouter, File, UploadFile
from fastapi.responses import StreamingResponse
from docx import Document

router = APIRouter()

reader = easyocr.Reader(["pt", "en"])

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


@router.post("/img-to-txt")
async def img_to_txt(arquivo: UploadFile = File(...)):
    """Cria documento txt com texto da imagem"""
    file_content = await arquivo.read()
    result = reader.readtext(file_content, paragraph=True, detail=0)

    nome_doc = Path(arquivo.filename).stem

    # considerar separar os paragrafos com duas linhas de distancia (so ta com uma por enquanto)
    output = StringIO("\n".join(result))

    return StreamingResponse(
        output,
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename={nome_doc}.txt"},
    )
