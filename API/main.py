from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from models import *
from routes import usuarios, restaurantes, pedidos, pagos, calificaciones, upload

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Restaurantes API",
    description="API para pedidos, pagos y calificaciones de restaurantes",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(usuarios.router)
app.include_router(restaurantes.router)
app.include_router(pedidos.router)
app.include_router(pagos.router)
app.include_router(calificaciones.router)
app.include_router(upload.router)

@app.get("/", tags=["Root"])
def root():
    return {"mensaje": "Restaurantes API funcionando ✅"}
