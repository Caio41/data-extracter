from io import BytesIO, StringIO
from pathlib import Path
from fastapi import APIRouter, File, UploadFile
from fastapi.responses import StreamingResponse
from docx import Document
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


@router.post('/testeeeee')
async def teste(arquivo: UploadFile = File(...)):
    file_content = await arquivo.read()

    img = Image.open(BytesIO(file_content))
    dados = pytesseract.image_to_data(img, lang='por', output_type='data.frame')

    dados = dados[dados.conf != -1]
    linhas = dados.groupby('block_num')['text'].apply(list)
    #frase = ' '.join(linhas)
    confiancas = dados.groupby(['block_num'])['conf'].mean()

    # Pega o index dos que tem confiança abaixo de 80
    indexes = confiancas[confiancas < 80].index.tolist()


    for index in indexes:
        txt_impreciso = linhas[index]
        txt_impreciso = ' '.join(txt_impreciso)
        print(txt_impreciso)

    # passos que tem que ser feitos:
    # 1. separa o texto em blocos 
    # 2. calcula as confiancas por bloco
    # 3. se confianca < numero, chamar função que corrige texto impreciso
    # 4. remontar texto original pra passar pro doc


  #  print(dados.to_string())
   # print(linhas)

    #print(conf)
