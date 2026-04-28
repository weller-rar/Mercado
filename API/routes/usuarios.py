from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_session
from models import Usuario
from schemas import UsuarioCreate, UsuarioResponse
from typing import List

router = APIRouter()

@router.post("/usuarios", response_model=UsuarioResponse)
def crear_usuario(usuario: UsuarioCreate, session: Session = Depends(get_session)):
    nuevo = Usuario(**usuario.model_dump())
    session.add(nuevo)
    session.commit()
    session.refresh(nuevo)
    return nuevo

@router.get("/usuarios", response_model=List[UsuarioResponse])
def obtener_usuarios(session: Session = Depends(get_session)):
    return session.query(Usuario).all()

@router.get("/usuarios/{id}", response_model=UsuarioResponse)
def obtener_usuario(id: int, session: Session = Depends(get_session)):
    usuario = session.get(Usuario, id)
    if not usuario:
        raise HTTPException(status_code=404, detail="No existe")
    return usuario

@router.delete("/usuarios/{id}")
def eliminar_usuario(id: int, session: Session = Depends(get_session)):
    usuario = session.get(Usuario, id)
    if not usuario:
        raise HTTPException(status_code=404, detail="No existe")
    session.delete(usuario)
    session.commit()
    return {"mensaje": "eliminado"}


