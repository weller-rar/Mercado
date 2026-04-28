from fastapi import FastAPI
from database import engine, Base
from models import *
from routes.usuarios import router as usuarios_router

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(usuarios_router)