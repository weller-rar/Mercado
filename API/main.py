import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.auth import hash_password
from database import SessionLocal, engine, Base, get_session
from models import Usuario
from routes import usuarios, restaurantes, pedidos, pagos, calificaciones, upload, admin
from contextlib import asynccontextmanager

Base.metadata.create_all(bind=engine)


def crear_usuario_root():
    db = SessionLocal()
    try:
        root_usuario = db.query(Usuario).filter(
            Usuario.rol == "root"
        ).first()
        if not root_usuario:
            root_usuario = Usuario(
                telefono="00000000000",
                nombre="Root",
                contrasena=hash_password(os.getenv("PASWORD_ROOT")),
                rol="root",
            )
            db.add(root_usuario)
            db.commit()
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    crear_usuario_root()
    yield

app = FastAPI(
    lifespan=lifespan,
    title="Restaurantes API",
    description="API para pedidos, pagos y calificaciones de restaurantes",
    version="1.0.0",
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(usuarios.router)
app.include_router(restaurantes.router)
app.include_router(pedidos.router)
app.include_router(pagos.router)
app.include_router(calificaciones.router)
app.include_router(upload.router)
app.include_router(admin.router)

@app.get("/", tags=["Root"])
def root():
    return {"mensaje": "Restaurantes API funcionando ✅"}