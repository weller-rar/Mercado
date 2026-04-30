from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    telefono = Column(String, nullable=False)
    contrasena = Column(String, nullable=False)

class Restaurante(Base):
    __tablename__ = "restaurantes"

    id_restaurante = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(String, nullable=True)
    horario = Column(DateTime, nullable=False)
    calificacion_promedio = Column(Float, default=0.0)


class Menu(Base):
    __tablename__ = "menus"

    id_menu = Column(Integer, primary_key=True, index=True)
    id_restaurante = Column(Integer, ForeignKey("restaurantes.id_restaurante"), nullable=False)
    nombre_menu = Column(String, nullable=False)

    restaurante = relationship("Restaurante")


class Calificacion(Base):
    __tablename__ = "calificaciones"

    id_calificacion = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    id_restaurante = Column(Integer, ForeignKey("restaurantes.id_restaurante"), nullable=False)
    puntuacion = Column(Float, default=0.0)
    comentarios = Column(String, nullable=True)
    fecha = Column(DateTime, nullable=False)

    usuario = relationship("Usuario")
    restaurante = relationship("Restaurante")


class Pedido(Base):
    __tablename__ = "pedidos"

    id_pedido = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    id_restaurante = Column(Integer, ForeignKey("restaurantes.id_restaurante"), nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)
    estado = Column(Integer, nullable=False)

    usuario = relationship("Usuario")
    restaurante = relationship("Restaurante")


class Pago(Base):
    __tablename__ = "pagos"

    id_pago = Column(Integer, primary_key=True, index=True)
    id_pedido = Column(Integer, ForeignKey("pedidos.id_pedido"), nullable=False)
    metodo_pago = Column(String, nullable=False)
    estado_pago = Column(String, nullable=False)
    fecha_pago = Column(DateTime, nullable=False)
    monto = Column(Float, nullable=False)

    pedido = relationship("Pedido")


class Producto(Base):
    __tablename__ = "productos"

    id_producto = Column(Integer, primary_key=True, index=True)
    id_menu = Column(Integer, ForeignKey("menus.id_menu"), nullable=False)
    nombre = Column(String, nullable=False)
    descripcion = Column(String, nullable=True)
    precio = Column(Float, nullable=False)
    disponible = Column(Integer, nullable=False)

    menu = relationship("Menu")


class DetallePedido(Base):
    __tablename__ = "detalle_pedidos"

    id_detalle = Column(Integer, primary_key=True, index=True)
    id_pedido = Column(Integer, ForeignKey("pedidos.id_pedido"), nullable=False)
    id_producto = Column(Integer, ForeignKey("productos.id_producto"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Float, nullable=False)

    pedido = relationship("Pedido")
    producto = relationship("Producto")