from fastapi import FastAPI
from routes import data, tabelas

app = FastAPI()


app.include_router(data.router, prefix='/data', tags=['data'])
app.include_router(tabelas.router, prefix='/tabelas', tags=['tabelas'])