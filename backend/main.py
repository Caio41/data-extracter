from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import tabelas, documents, experimentos

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

app.include_router(tabelas.router, prefix="/tabelas", tags=["tabelas"])
app.include_router(experimentos.router, prefix="/experimentos", tags=["experimentos"])
app.include_router(documents.router, prefix="/documents", tags=["documents"])
