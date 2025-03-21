from fastapi import APIRouter, File, UploadFile
from fastapi.responses import StreamingResponse
import numpy as np
import cv2
from services.imagem_utils import extrair_tabela

router = APIRouter()

@router.post("/tesseract/")
async def tesseract_extrair_tabela(arquivo: UploadFile = File(...)) -> StreamingResponse:
    """Extrai tabela da imagem utilizando tesseract"""
    file_content = await arquivo.read()  
    np_array = np.frombuffer(file_content, np.uint8)  # Converte bytes para NumPy array
    imagem = cv2.imdecode(np_array, cv2.IMREAD_COLOR) # faz o decode da imagem usando cv2
    csv = extrair_tabela(imagem)

    return StreamingResponse(
        csv,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=output.csv"},
    )