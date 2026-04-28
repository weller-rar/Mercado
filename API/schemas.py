from pydantic import BaseModel
from typing import Optional

class UsuarioCreate(BaseModel):
    nombre: str
    telefono: str

class UsuarioResponse(BaseModel):
    id_usuario: int
    nombre: str
    telefono: str

    class Config:
        from_attributes = True