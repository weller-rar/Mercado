from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_session
import models, schemas
from routes.auth import get_current_user

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])

ESTADOS = {0: "pendiente", 1: "en preparación", 2: "en camino", 3: "entregado", 4: "cancelado"}


# ─── Pedidos ──────────────────────────────────────────────────────────────────

@router.post("/", response_model=schemas.PedidoResponse, status_code=status.HTTP_201_CREATED)
def crear_pedido(
    datos: schemas.PedidoCreate,
    db: Session = Depends(get_session),
    usuario_actual: models.Usuario = Depends(get_current_user),
):
    restaurante = db.query(models.Restaurante).filter(
        models.Restaurante.id_restaurante == datos.id_restaurante
    ).first()
    if not restaurante:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")

    pedido = models.Pedido(
        id_usuario=usuario_actual.id_usuario,
        id_restaurante=datos.id_restaurante,
        estado=0,
    )
    db.add(pedido)
    db.commit()
    db.refresh(pedido)
    return pedido


@router.get("/", response_model=list[schemas.PedidoResponse])
def listar_pedidos(
    db: Session = Depends(get_session),
    usuario_actual: models.Usuario = Depends(get_current_user),
):
    return db.query(models.Pedido).filter(
        models.Pedido.id_usuario == usuario_actual.id_usuario
    ).all()


@router.get("/{id_pedido}", response_model=schemas.PedidoResponse)
def obtener_pedido(
    id_pedido: int,
    db: Session = Depends(get_session),
    usuario_actual: models.Usuario = Depends(get_current_user),
):
    pedido = db.query(models.Pedido).filter(
        models.Pedido.id_pedido == id_pedido,
        models.Pedido.id_usuario == usuario_actual.id_usuario,
    ).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return pedido


@router.patch("/{id_pedido}/estado", response_model=schemas.PedidoResponse)
def actualizar_estado(
    id_pedido: int,
    estado: int,
    db: Session = Depends(get_session),
    _=Depends(get_current_user),
):
    if estado not in ESTADOS:
        raise HTTPException(
            status_code=400,
            detail=f"Estado inválido. Opciones: {ESTADOS}",
        )
    pedido = db.query(models.Pedido).filter(models.Pedido.id_pedido == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    pedido.estado = estado
    db.commit()
    db.refresh(pedido)
    return pedido


@router.delete("/{id_pedido}", status_code=status.HTTP_204_NO_CONTENT)
def cancelar_pedido(
    id_pedido: int,
    db: Session = Depends(get_session),
    usuario_actual: models.Usuario = Depends(get_current_user),
):
    pedido = db.query(models.Pedido).filter(
        models.Pedido.id_pedido == id_pedido,
        models.Pedido.id_usuario == usuario_actual.id_usuario,
    ).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    if pedido.estado not in (0, 1):
        raise HTTPException(status_code=400, detail="No se puede cancelar un pedido en este estado")
    pedido.estado = 4  # cancelado
    db.commit()


# ─── Detalle de Pedido ────────────────────────────────────────────────────────

@router.get("/{id_pedido}/detalle", response_model=list[schemas.DetallePedidoResponse])
def listar_detalle(
    id_pedido: int,
    db: Session = Depends(get_session),
    _=Depends(get_current_user),
):
    return db.query(models.DetallePedido).filter(
        models.DetallePedido.id_pedido == id_pedido
    ).all()


@router.post("/{id_pedido}/detalle", response_model=schemas.DetallePedidoResponse, status_code=status.HTTP_201_CREATED)
def agregar_detalle(
    id_pedido: int,
    datos: schemas.DetallePedidoCreate,
    db: Session = Depends(get_session),
    usuario_actual: models.Usuario = Depends(get_current_user),
):
    pedido = db.query(models.Pedido).filter(
        models.Pedido.id_pedido == id_pedido,
        models.Pedido.id_usuario == usuario_actual.id_usuario,
    ).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    if pedido.estado != 0:
        raise HTTPException(status_code=400, detail="Solo se pueden agregar items a pedidos pendientes")

    producto = db.query(models.Producto).filter(
        models.Producto.id_producto == datos.id_producto
    ).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    if not producto.disponible:
        raise HTTPException(status_code=400, detail="Producto no disponible")

    detalle = models.DetallePedido(
        id_pedido=id_pedido,
        id_producto=datos.id_producto,
        cantidad=datos.cantidad,
        precio_unitario=producto.precio,
    )
    db.add(detalle)
    db.commit()
    db.refresh(detalle)
    return detalle


@router.delete("/{id_pedido}/detalle/{id_detalle}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_detalle(
    id_pedido: int,
    id_detalle: int,
    db: Session = Depends(get_session),
    usuario_actual: models.Usuario = Depends(get_current_user),
):
    pedido = db.query(models.Pedido).filter(
        models.Pedido.id_pedido == id_pedido,
        models.Pedido.id_usuario == usuario_actual.id_usuario,
    ).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    detalle = db.query(models.DetallePedido).filter(
        models.DetallePedido.id_detalle == id_detalle,
        models.DetallePedido.id_pedido == id_pedido,
    ).first()
    if not detalle:
        raise HTTPException(status_code=404, detail="Detalle no encontrado")
    db.delete(detalle)
    db.commit()
