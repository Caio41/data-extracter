import os
import cv2
import numpy as np

def converte_para_grayscale(imagem):
    return cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)

def limiar_imagem(imagem):
    return cv2.threshold(imagem, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

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

def encontra_maior_borda(bordas_retangulares, imagem): # Encontra maior borda da imagem
    maior_borda = max(bordas_retangulares, key=cv2.contourArea, default=None)
    imagem_com_borda = imagem.copy()
    if maior_borda is not None:
        cv2.drawContours(imagem_com_borda, [maior_borda], -1, (0, 255, 0), 3)
    return maior_borda, imagem_com_borda

def acha_vertices(borda):
    borda = borda.reshape(4, 2)
    rect = np.zeros((4, 2), dtype="float32")
    s = borda.sum(axis=1)
    diff = np.diff(borda, axis=1)
    rect[0], rect[2] = borda[np.argmin(s)], borda[np.argmax(s)]
    rect[1], rect[3] = borda[np.argmin(diff)], borda[np.argmax(diff)]
    return rect

def transforma_perspectiva(imagem, borda):
    vertices = acha_vertices(borda)
    width = int(np.linalg.norm(vertices[0] - vertices[1]))
    height = int(np.linalg.norm(vertices[0] - vertices[3]))
    pontos_destino = np.array([[0, 0], [width, 0], [width, height], [0, height]], dtype="float32")
    matrix = cv2.getPerspectiveTransform(vertices, pontos_destino)
    return cv2.warpPerspective(imagem, matrix, (width, height))

def add_padding(image, padding_ratio=0.1):
    pad = int(image.shape[0] * padding_ratio)
    return cv2.copyMakeBorder(image, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=[255, 255, 255])

def save_image(path, imagem):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    cv2.imwrite(path, imagem)


def extrair_tabela(imagem, save_dir='./imagens_processadas/' ):
    imagem_grayscale = converte_para_grayscale(imagem)
    imagem_limiar = limiar_imagem(imagem_grayscale)
    imagem_invertida = inverter_imagem(imagem_limiar)
    imagem_dilatada = dilatar_imagem(imagem_invertida)
    bordas, imagem_com_bordas = enconta_bordas(imagem_dilatada)
    bordas_retangulares, imagem_com_retangulos = filtra_bordas_retangulares(bordas, imagem)
    maior_borda, imagem_com_maior_borda = encontra_maior_borda(bordas_retangulares, imagem)
    if maior_borda is None:
        return None
    imagem_transformada = transforma_perspectiva(imagem, maior_borda)
    imagem_final = add_padding(imagem_transformada)

    save_image(save_dir + "0_original.jpg", imagem)
    save_image(save_dir + "1_grayscale.jpg", imagem_grayscale)
    save_image(save_dir + "2_limiar.jpg", imagem_limiar)
    save_image(save_dir + "3_invertida.jpg", imagem_invertida)
    save_image(save_dir + "4_dilatada.jpg", imagem_dilatada)
    save_image(save_dir + "5_com_bordas.jpg", imagem_com_bordas)
    save_image(save_dir + "6_retangulos.jpg", imagem_com_retangulos)
    save_image(save_dir + "7_maior_borda.jpg", imagem_com_maior_borda)
    save_image(save_dir + "8_transformada.jpg", imagem_transformada)
    save_image(save_dir + "9_final.jpg", imagem_final)

    print('a')
    return imagem_final



