from fastapi import FastAPI
from database import engine, Base
from models import *
from routes import usuarios, restaurantes, pedidos, pagos, calificaciones

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Restaurantes API",
    description="API para pedidos, pagos y calificaciones de restaurantes",
    version="1.0.0",
)

app.include_router(usuarios.router)
app.include_router(restaurantes.router)
app.include_router(pedidos.router)
app.include_router(pagos.router)
app.include_router(calificaciones.router)


@app.get("/", tags=["Root"])
def root():
    return {"mensaje": "Restaurantes API funcionando ✅"}
