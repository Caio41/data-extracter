from fastapi import FastAPI
from routes import documents, experimentos

app = FastAPI()


app.include_router(experimentos.router, prefix='/experimentos', tags=['experimentos'])
app.include_router(documents.router, prefix='/documents', tags=['documents'])