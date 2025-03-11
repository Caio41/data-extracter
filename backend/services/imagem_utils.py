import io
import os
import cv2
import numpy as np
import subprocess
import tempfile
from fastapi import HTTPException, status

def converte_para_grayscale(imagem):
    return cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)

def limiar_imagem(imagem, limite):
    return cv2.threshold(imagem, limite, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

def limiar_imagem2(imagem, limite):
    return cv2.threshold(imagem, limite, 255, cv2.THRESH_BINARY)[1]

def inverter_imagem(imagem):
    return cv2.bitwise_not(imagem)

def dilatar_imagem(imagem):
    return cv2.dilate(imagem, None, iterations=5)

def enconta_bordas(imagem):
    bordas, _ = cv2.findContours(imagem, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    imagem_com_bordas = imagem.copy()
    cv2.drawContours(imagem_com_bordas, bordas, -1, (0, 255, 0), 3)
    return bordas, imagem_com_bordas

def filtra_bordas_retangulares(bordas, imagem):
    bordas_retangulares = []
    
    for borda in bordas:
        perimetro = cv2.arcLength(borda, True)
        aproximado = cv2.approxPolyDP(borda, 0.02 * perimetro, True)
        
        if len(aproximado) == 4:
            bordas_retangulares.append(aproximado)

    imagem_com_retangulos = imagem.copy()
    cv2.drawContours(imagem_com_retangulos, bordas_retangulares, -1, (0, 255, 0), 3) # desenha em verde as bordas na imagem originsl
    return bordas_retangulares, imagem_com_retangulos

def get_maior_borda(bordas_retangulares, imagem): # Encontra maior borda da imagem
    maior_borda = max(bordas_retangulares, key=cv2.contourArea, default=None)
    imagem_com_borda = imagem.copy()
    if maior_borda is not None:
        cv2.drawContours(imagem_com_borda, [maior_borda], -1, (0, 255, 0), 3)
    return maior_borda, imagem_com_borda

def get_vertices(borda):
    borda = borda.reshape(4, 2)
    rect = np.zeros((4, 2), dtype="float32")
    s = borda.sum(axis=1)
    diff = np.diff(borda, axis=1)
    rect[0], rect[2] = borda[np.argmin(s)], borda[np.argmax(s)]
    rect[1], rect[3] = borda[np.argmin(diff)], borda[np.argmax(diff)]
    return rect

def transforma_perspectiva(imagem, borda):
    vertices = get_vertices(borda)
    width = int(np.linalg.norm(vertices[0] - vertices[1]))
    height = int(np.linalg.norm(vertices[0] - vertices[3]))
    pontos_destino = np.array([[0, 0], [width, 0], [width, height], [0, height]], dtype="float32")
    matrix = cv2.getPerspectiveTransform(vertices, pontos_destino)
    return cv2.warpPerspective(imagem, matrix, (width, height))

def add_padding(imagem, padding_ratio=0.1):
    pad = int(imagem.shape[0] * padding_ratio)
    return cv2.copyMakeBorder(imagem, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=[255, 255, 255])

def erosao_linhas_verticais(imagem):
    hor = np.array([[1,1,1,1,1,1]], dtype=np.uint8)
    eroded = cv2.erode(imagem, hor, iterations=10)
    return cv2.dilate(eroded, hor, iterations=10)

def erosao_linhas_horizontais(imagem):
    ver = np.array([[1], [1], [1], [1], [1], [1], [1]], dtype=np.uint8)
    eroded = cv2.erode(imagem, ver, iterations=10)
    return cv2.dilate(eroded, ver, iterations=10)

def combina_imagens(vertical, horizontal):
    return cv2.add(vertical, horizontal)

def dilata_imagem_combinada(imagem):
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    return cv2.dilate(imagem, kernel, iterations=5)

def subtrai_imagem(imagem1, imagem2):
    return cv2.subtract(imagem1, imagem2)

def remove_ruido(imagem):
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    eroded = cv2.erode(imagem, kernel, iterations=1)
    return cv2.dilate(eroded, kernel, iterations=1)

def dilata_palavras(imagem):
    kernel = np.array([[1] * 10] * 2, dtype=np.uint8)
    dilated = cv2.dilate(imagem, kernel, iterations=5)
    simple_kernel = np.ones((5, 5), np.uint8)
    return cv2.dilate(dilated, simple_kernel, iterations=2)

def get_bordas_palavras(imagem_dilatada, imagem_original):
    bordas, _ = cv2.findContours(imagem_dilatada, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    imagem_com_bordas = imagem_original.copy()
    cv2.drawContours(imagem_com_bordas, bordas, -1, (0, 255, 0), 3)
    return bordas, imagem_com_bordas

def segmenta_imagem(bordas, imagem_original):
    segmentos = []
    image_com_segmentos = imagem_original.copy()
    for contour in bordas:
        x, y, w, h = cv2.boundingRect(contour)
        segmentos.append((x, y, w, h))
        cv2.rectangle(image_com_segmentos, (x, y), (x + w, y + h), (0, 255, 0), 5)
    return segmentos, image_com_segmentos

def get_altura_media_segmentos(segmentos):
    heights = [h for _, _, _, h in segmentos]
    return np.mean(heights)

def ordena_segmentos_y(segmentos):
    return sorted(segmentos, key=lambda x: x[1])

def organiza_segmentos_em_linhas(segmentos, altura_media):
    linhas = []
    half_height = altura_media / 2
    current_linha = [segmentos[0]]

    for box in segmentos[1:]:
        if abs(box[1] - current_linha[-1][1]) <= half_height:
            current_linha.append(box)
        else:
            linhas.append(current_linha)
            current_linha = [box]

    linhas.append(current_linha)
    return linhas

def ordena_linhas_x(linhas):
    return [sorted(linha, key=lambda x: x[0]) for linha in linhas]

def get_result_from_tesseract(imagem):
    with tempfile.NamedTemporaryFile(suffix=".png", delete=True) as temp_file:
        temp_filename = temp_file.name
        cv2.imwrite(temp_filename, imagem)

        output = subprocess.getoutput(
            f'tesseract {temp_filename} - -l eng+por --oem 3 --psm 7 --dpi 72'
        )
    
    return output.strip()

def get_tabela(imagem_original, linhas, save_dir="./imagens_segmentadas/"):
    os.makedirs(save_dir, exist_ok=True)
    table = []
    image_number = 0

    for linha in linhas:
        linha_atual = []
        for x, y, w, h in linha:
            y = max(0, y - 5) 
            cropped_image = imagem_original[y:y + h, x:x + w]
            image_slice_path = os.path.join(save_dir, f"img_{image_number}.jpg")
            cv2.imwrite(image_slice_path, cropped_image)
            ocr_result = get_result_from_tesseract(cropped_image)
            linha_atual.append(ocr_result)
            image_number += 1
        table.append(linha_atual)

    return table


def get_csv(tabela, output_file="output_tabela.csv"):
    csv_output = io.StringIO()
    for row in tabela:
        csv_output.write(",".join(row) + "\n")
    csv_output.seek(0)
    return csv_output

def save_image(path, imagem):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    cv2.imwrite(path, imagem)


def extrair_tabela(imagem, save_dir='./imagens_processadas/' ):
    imagem_grayscale = converte_para_grayscale(imagem)
    imagem_limiar = limiar_imagem(imagem_grayscale, 0)
    imagem_invertida = inverter_imagem(imagem_limiar)
    imagem_dilatada = dilatar_imagem(imagem_invertida)
    bordas, imagem_com_bordas = enconta_bordas(imagem_dilatada)
    bordas_retangulares, imagem_com_retangulos = filtra_bordas_retangulares(bordas, imagem)
    maior_borda, imagem_com_maior_borda = get_maior_borda(bordas_retangulares, imagem)
    if maior_borda is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Não foi identificada uma tabela na imagem")
    imagem_transformada = transforma_perspectiva(imagem, maior_borda)
    imagem_tabela = add_padding(imagem_transformada)
    imagem_tabela_grayscale = converte_para_grayscale(imagem_tabela)
    imagem_tabela_limiar = limiar_imagem2(imagem_tabela_grayscale, 127)
    imagem_tabela_invertida = inverter_imagem(imagem_tabela_limiar)
    imagem_erosao_vertical = erosao_linhas_verticais(imagem_tabela_invertida)
    imagem_erosao_horizontal = erosao_linhas_horizontais(imagem_tabela_invertida)
    imagem_erosao_combinada = combina_imagens(imagem_erosao_vertical, imagem_erosao_horizontal)
    imagem_combinada_dilatada = dilata_imagem_combinada(imagem_erosao_combinada)
    imagem_subtraida = subtrai_imagem(imagem_tabela_invertida, imagem_combinada_dilatada)
    imagem_sem_ruido = remove_ruido(imagem_subtraida)
    imagem_palavra_dilatada = dilata_palavras(imagem_sem_ruido)
    bordas_palavras, imagem_bordas_palavras = get_bordas_palavras(imagem_palavra_dilatada, imagem_tabela)
    segmentos, imagem_com_segmentos = segmenta_imagem(bordas_palavras, imagem_tabela)
    altura_media = get_altura_media_segmentos(segmentos)
    segmentos_ordenados = ordena_segmentos_y(segmentos)
    if len(segmentos_ordenados) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Não foi identificada uma tabela na imagem")
    linhas = organiza_segmentos_em_linhas(segmentos_ordenados, altura_media)
    linhas_ordenadas = ordena_linhas_x(linhas)
    tabela = get_tabela(imagem_tabela, linhas_ordenadas)
    csv = get_csv(tabela)





    save_image(save_dir + "0_original.jpg", imagem)
    save_image(save_dir + "1_grayscale.jpg", imagem_grayscale)
    save_image(save_dir + "2_limiar.jpg", imagem_limiar)
    save_image(save_dir + "3_invertida.jpg", imagem_invertida)
    save_image(save_dir + "4_dilatada.jpg", imagem_dilatada)
    save_image(save_dir + "5_com_bordas.jpg", imagem_com_bordas)
    save_image(save_dir + "6_retangulos.jpg", imagem_com_retangulos)
    save_image(save_dir + "7_maior_borda.jpg", imagem_com_maior_borda)
    save_image(save_dir + "8_transformada.jpg", imagem_transformada)
    save_image(save_dir + "9_tabela.jpg", imagem_tabela)
    save_image(save_dir + "10_tabela_grayscale.jpg", imagem_tabela_grayscale)
    save_image(save_dir + "11_tabela_limiar.jpg", imagem_tabela_limiar)
    save_image(save_dir + "12_tabela_invertida.jpg", imagem_tabela_invertida)
    save_image(save_dir + "13_erosao_vertical.jpg", imagem_erosao_vertical)
    save_image(save_dir + "14_erosao_horizontal.jpg", imagem_erosao_horizontal)
    save_image(save_dir + "15_erosao_combinada.jpg", imagem_erosao_combinada)
    save_image(save_dir + "16_combinada_dilatada.jpg", imagem_combinada_dilatada)
    save_image(save_dir + "17_subtraida.jpg", imagem_subtraida)
    save_image(save_dir + "18_sem_ruido.jpg", imagem_sem_ruido)
    save_image(save_dir + "19_palavra_dilatada.jpg", imagem_palavra_dilatada)
    save_image(save_dir + "20_bordas_palavras.jpg", imagem_bordas_palavras)
    save_image(save_dir + "21_segmentos.jpg", imagem_com_segmentos)

    return csv



