# Data Extracter
API para extração de texto e tabelas a partir de imagens

## Features
- Extrair texto de uma imagem e exportar para docx
- Extrair texto de uma imagem e exportar para txt
- Extrair tabelas de uma imagem e exportar para csv
- Pós-processamento do texto encontrado utilizando LLMs
- Suporte para imagens do tipo: png, jpg, tiff e PDF com imagens.


## Dependências
As dependências do projeto são gerenciadas pela ferramenta poetry, que pode ser instalada [aqui](https://python-poetry.org/docs/#installing-with-pipx).

Para instalar as dependências, use:
```sh
cd /backend
# Instala dependências
poetry install

# Ativa venv
poetry shell
```

Além disso, também é necessário instalar as ferramentas [Tesseract](https://tesseract-ocr.github.io/tessdoc/Downloads) e [GhostScript](https://ghostscript.com/releases/gsdnld.html)

## Uso
Para configurar o front-end:

`cd frontend/data-extracter`

Duplique o arquivo `.env.example` e renomeie a cópia para `.env.local`
Na variável de ambiente `NEXT_PUBLIC_BACKEND_URL`, dentro do arquivo, deve ser inserida a URL do backend. O padrão é manter o valor que já está.

Em seguida, para rodar o front:
```
npm install
npm run dev
```

Para configurar o backend:

`cd backend`

Será necessário a criação de um arquivo .env com a seguinte variável:
```dotenv
OPENAI_KEY=INSERIR_CHAVE_OPENAI
```


Por fim, para rodar o backend:
```
uvicorn main:app
```



## Tecnologias utilizadas
- Python
- FastAPI
- Tesseract
- pymupdf
- OpenAI
