# Textracter
API para extração de texto e tabelas a partir de imagens

## Demonstração


## Features
- Extrair texto de uma imagem e exportar para docx
- Extrair texto de uma imagem e exportar para txt
- Extrair tabelas de uma imagem e exportar para Excel
- Suporte para imagens do tipo: png, jpg, tiff e PDF com imagens.


## Dependências
As dependências do projeto são gerenciadas pela ferramenta poetry, que pode ser instalada [aqui](https://python-poetry.org/docs/#installing-with-pipx).

Para instalar as dependências, use:
```sh
# Instala dependências
poetry install

# Ativa venv
poetry shell
```



## Uso
Para rodar o frontend, use:
```
npm install
npm run dev
```

Para rodar o backend, use:
```
uvicorn main:app
```



## Tecnologias utilizadas
- Python
- FastAPI
- Tesseract
- fitz
