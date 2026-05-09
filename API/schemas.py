from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class RestauranteAdmin(BaseModel):
    id_restaurante: int
    id_comercial: str
    nombre: str
    descripcion: Optional[str]
    horario: Optional[str]
    calificacion_promedio: float
    estado: bool
    imagen_url: Optional[str] = None
    class Config:
        from_attributes = True

# ─── Calificacion ─────────────────────────────────────────────────────────────
class CalificacionCreate(BaseModel):
    id_restaurante: int
    puntuacion: float
    comentarios: Optional[str] = None

class CalificacionResponse(BaseModel):
    id_calificacion: int
    id_usuario: int
    id_restaurante: int
    puntuacion: float
    comentarios: Optional[str]
    fecha: datetime
    class Config:
        from_attributes = True


# ─── Administrador ───────────────────────────────────────────────────────────
class LoginAdministrador(BaseModel):
    nombre: str
    contrasena: str

# ─── Usuario ──────────────────────────────────────────────────────────────────
class LoginInvitado(BaseModel):
    telefono: str

class LoginRestauranteSchema(BaseModel):
    id_comercial: str
    contrasena: str

class UsuarioCreate(BaseModel):
    nombre: Optional[str] = None
    telefono: str
    contrasena: Optional[str] = None
    rol: str = "cliente"

class UsuarioResponse(BaseModel):
    id_usuario: int
    nombre: Optional[str]
    telefono: str
    rol: str
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    rol: str

class TokenRestaurante(BaseModel):
    access_token: str
    token_type: str
    id_restaurante: int
    id_comercial: str
    nombre: str


# ─── Restaurante ──────────────────────────────────────────────────────────────
class RestauranteCreate(BaseModel):
    id_comercial: str
    nombre: str
    descripcion: Optional[str] = None
    horario: Optional[str] = None
    contrasena: str

class RestaurantePublico(BaseModel):
    id_restaurante: int
    id_comercial: str
    nombre: str
    descripcion: Optional[str]
    horario: Optional[str]
    calificacion_promedio: float
    imagen_url: Optional[str] = None
    class Config:
        from_attributes = True

class RestauranteResponse(RestaurantePublico):
    estado: bool
    class Config:
        from_attributes = True

class ActualizarInfoBasica(BaseModel):
    descripcion: Optional[str] = None
    horario: Optional[str] = None

class ActualizarNombreSchema(BaseModel):
    nombre: str
    id_comercial: str
    contrasena: str


# ─── Menú / Producto ──────────────────────────────────────────────────────────
class MenuCreate(BaseModel):
    id_restaurante: int
    nombre_menu: str

class MenuResponse(MenuCreate):
    id_menu: int
    class Config:
        from_attributes = True

class ProductoCreate(BaseModel):
    id_menu: int
    nombre: str
    descripcion: Optional[str] = None
    precio: float
    disponible: int = 1

class ProductoResponse(ProductoCreate):
    id_producto: int
    imagen_url: Optional[str] = None
    class Config:
        from_attributes = True

class ToggleDisponibilidad(BaseModel):
    disponible: bool


# ─── Carrito / Checkout ───────────────────────────────────────────────────────
class ItemCarrito(BaseModel):
    id_producto: int
    cantidad: int

class CheckoutRequest(BaseModel):
    """El cliente envía su carrito completo con el método de pago."""
    items: List[ItemCarrito]
    metodo_pago: str   # 'efectivo' | 'nequi' | 'tarjeta' | 'daviplata'

class DetallePedidoResponse(BaseModel):
    id_detalle: int
    id_producto: int
    cantidad: int
    precio_unitario: float
    nombre_producto: Optional[str] = None
    imagen_producto: Optional[str] = None
    class Config:
        from_attributes = True

class PedidoResponse(BaseModel):
    id_pedido: int
    id_restaurante: int
    nombre_restaurante: Optional[str] = None
    numero_orden: Optional[str]
    fecha: datetime
    estado: int
    metodo_pago: Optional[str] = None
    detalles: List[DetallePedidoResponse] = []
    total: float = 0.0
    class Config:
        from_attributes = True

class TransaccionResponse(BaseModel):
    id_transaccion: int
    fecha: datetime
    metodo_pago: str
    total: float
    pedidos: List[PedidoResponse] = []
    class Config:
        from_attributes = True

class ActualizarEstado(BaseModel):
    estado: int


# ─── Calificacion ─────────────────────────────────────────────────────────────
class CalificacionCreate(BaseModel):
    id_restaurante: int
    puntuacion: float
    comentarios: Optional[str] = None

class CalificacionResponse(CalificacionCreate):
    id_calificacion: int
    id_usuario: int
    fecha: datetime
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
