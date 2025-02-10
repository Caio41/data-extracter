from fastapi import FastAPI
from routes import data

app = FastAPI()


app.include_router(data.router, prefix='/data', tags=['data'])