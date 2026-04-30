from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# ─── Usuario ──────────────────────────────────────────────────────────────────

class UsuarioCreate(BaseModel):
    nombre: str
    telefono: str
    contrasena: str

class UsuarioResponse(BaseModel):
    id_usuario: int
    nombre: str
    telefono: str

    class Config:
        from_attributes = True


# ─── Restaurante ──────────────────────────────────────────────────────────────

class RestauranteCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    horario: datetime

class RestauranteResponse(RestauranteCreate):
    id_restaurante: int
    calificacion_promedio: float

    class Config:
        from_attributes = True


# ─── Menu ─────────────────────────────────────────────────────────────────────

class MenuCreate(BaseModel):
    id_restaurante: int
    nombre_menu: str

class MenuResponse(MenuCreate):
    id_menu: int

    class Config:
        from_attributes = True


# ─── Producto ─────────────────────────────────────────────────────────────────

class ProductoCreate(BaseModel):
    id_menu: int
    nombre: str
    descripcion: Optional[str] = None
    precio: float
    disponible: int = 1

class ProductoResponse(ProductoCreate):
    id_producto: int

    class Config:
        from_attributes = True


# ─── Calificacion ─────────────────────────────────────────────────────────────

class CalificacionCreate(BaseModel):
    id_usuario: int
    id_restaurante: int
    puntuacion: float
    comentarios: Optional[str] = None
    fecha: datetime

class CalificacionResponse(CalificacionCreate):
    id_calificacion: int

    class Config:
        from_attributes = True


# ─── Pedido ───────────────────────────────────────────────────────────────────

class PedidoCreate(BaseModel):
    id_usuario: int
    id_restaurante: int
    estado: int = 0

class PedidoResponse(PedidoCreate):
    id_pedido: int
    fecha: datetime

    class Config:
        from_attributes = True


# ─── DetallePedido ────────────────────────────────────────────────────────────

class DetallePedidoCreate(BaseModel):
    id_pedido: int
    id_producto: int
    cantidad: int
    precio_unitario: float

class DetallePedidoResponse(DetallePedidoCreate):
    id_detalle: int

    class Config:
        from_attributes = True


# ─── Pago ─────────────────────────────────────────────────────────────────────

class PagoCreate(BaseModel):
    id_pedido: int
    metodo_pago: str
    estado_pago: str
    fecha_pago: datetime
    monto: float

class PagoResponse(PagoCreate):
    id_pago: int

    class Config:
        from_attributes = True


# ─── Auth ─────────────────────────────────────────────────────────────────────

class Token(BaseModel):
    access_token: str
    token_type: str
