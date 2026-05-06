from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class Usuario(Base):
    __tablename__ = "usuarios"
    id_usuario  = Column(Integer, primary_key=True, index=True)
    nombre      = Column(String, nullable=True)
    telefono    = Column(String, nullable=False, unique=True)
    contrasena  = Column(String, nullable=True)
    rol         = Column(String, nullable=False, default="cliente")


class Restaurante(Base):
    __tablename__ = "restaurantes"
    id_restaurante      = Column(Integer, primary_key=True, index=True)
    id_comercial        = Column(String, unique=True, nullable=False)
    nombre              = Column(String, nullable=False)
    descripcion         = Column(String, nullable=True)
    horario             = Column(String, nullable=True)
    calificacion_promedio = Column(Float, default=0.0)
    contrasena          = Column(String, nullable=False)
    estado              = Column(Boolean, nullable=False, default=False)
    imagen_url          = Column(String, nullable=True)


class Menu(Base):
    __tablename__ = "menus"
    id_menu        = Column(Integer, primary_key=True, index=True)
    id_restaurante = Column(Integer, ForeignKey("restaurantes.id_restaurante"), nullable=False)
    nombre_menu    = Column(String, nullable=False)
    restaurante    = relationship("Restaurante")


class Producto(Base):
    __tablename__ = "productos"
    id_producto = Column(Integer, primary_key=True, index=True)
    id_menu     = Column(Integer, ForeignKey("menus.id_menu"), nullable=False)
    nombre      = Column(String, nullable=False)
    descripcion = Column(String, nullable=True)
    precio      = Column(Float, nullable=False)
    disponible  = Column(Integer, nullable=False)
    imagen_url  = Column(String, nullable=True)
    menu        = relationship("Menu")


class Transaccion(Base):
    """Agrupa todos los pedidos de una misma compra (puede ser multirestaurante)."""
    __tablename__ = "transacciones"
    id_transaccion = Column(Integer, primary_key=True, index=True)
    id_usuario     = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    fecha          = Column(DateTime, default=datetime.utcnow)
    metodo_pago    = Column(String, nullable=False)
    total          = Column(Float, nullable=False, default=0.0)
    usuario        = relationship("Usuario")
    pedidos        = relationship("Pedido", back_populates="transaccion")


class Pedido(Base):
    """
    estados:
      1 = Pendiente de pago (efectivo)
      2 = En preparación
      3 = Listo para recoger
      4 = Entregado
      5 = Cancelado
    """
    __tablename__ = "pedidos"
    id_pedido      = Column(Integer, primary_key=True, index=True)
    id_usuario     = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    id_restaurante = Column(Integer, ForeignKey("restaurantes.id_restaurante"), nullable=False)
    id_transaccion = Column(Integer, ForeignKey("transacciones.id_transaccion"), nullable=True)
    numero_orden   = Column(String, nullable=True)
    fecha          = Column(DateTime, default=datetime.utcnow)
    estado         = Column(Integer, nullable=False, default=1)
    usuario        = relationship("Usuario")
    restaurante    = relationship("Restaurante")
    transaccion    = relationship("Transaccion", back_populates="pedidos")
    detalles       = relationship("DetallePedido", back_populates="pedido")


class DetallePedido(Base):
    __tablename__ = "detalle_pedidos"
    id_detalle      = Column(Integer, primary_key=True, index=True)
    id_pedido       = Column(Integer, ForeignKey("pedidos.id_pedido"), nullable=False)
    id_producto     = Column(Integer, ForeignKey("productos.id_producto"), nullable=False)
    cantidad        = Column(Integer, nullable=False)
    precio_unitario = Column(Float, nullable=False)
    pedido          = relationship("Pedido", back_populates="detalles")
    producto        = relationship("Producto")


class Calificacion(Base):
    __tablename__ = "calificaciones"
    id_calificacion = Column(Integer, primary_key=True, index=True)
    id_usuario      = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    id_restaurante  = Column(Integer, ForeignKey("restaurantes.id_restaurante"), nullable=False)
    puntuacion      = Column(Float, default=0.0)
    comentarios     = Column(String, nullable=True)
    fecha           = Column(DateTime, nullable=False)
    usuario         = relationship("Usuario")
    restaurante     = relationship("Restaurante")


class Pago(Base):
    __tablename__ = "pagos"
    id_pago      = Column(Integer, primary_key=True, index=True)
    id_pedido    = Column(Integer, ForeignKey("pedidos.id_pedido"), nullable=False)
    metodo_pago  = Column(String, nullable=False)
    estado_pago  = Column(String, nullable=False)
    fecha_pago   = Column(DateTime, nullable=False)
    monto        = Column(Float, nullable=False)
    pedido       = relationship("Pedido")
