# Textracter
API para extração de texto e tabelas a partir de imagens

## Demonstração


## Features
- Extrair texto de uma imagem e exportar para docx
- Extrair texto de uma imagem e exportar para txt
- Extrair tabelas de uma imagem e exportar para Excel
- Suporte para imagens do tipo: png, jpg, tiff e PDF com imagens.


## Dependências


## Uso
Para ativar o frontend, use:
```
npm install
```
```
npm run dev
```

Para ativar o backend, use:
```
poetry shell
```
```
uvicorn main:app
```



## Tecnologias utilizadas
- Python
- FastAPI
- Tesseract
- fitz
