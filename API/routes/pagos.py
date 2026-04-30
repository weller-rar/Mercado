from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_session
import models, schemas
from routes.auth import get_current_user

router = APIRouter(prefix="/pagos", tags=["Pagos"])

METODOS_VALIDOS = {"efectivo", "tarjeta", "transferencia", "nequi", "daviplata"}


@router.post("/", response_model=schemas.PagoResponse, status_code=status.HTTP_201_CREATED)
def crear_pago(
    datos: schemas.PagoCreate,
    db: Session = Depends(get_session),
    usuario_actual: models.Usuario = Depends(get_current_user),
):
    if datos.metodo_pago not in METODOS_VALIDOS:
        raise HTTPException(
            status_code=400,
            detail=f"Método de pago inválido. Opciones: {METODOS_VALIDOS}",
        )

    pedido = db.query(models.Pedido).filter(
        models.Pedido.id_pedido == datos.id_pedido,
        models.Pedido.id_usuario == usuario_actual.id_usuario,
    ).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    ya_pagado = db.query(models.Pago).filter(
        models.Pago.id_pedido == datos.id_pedido,
        models.Pago.estado_pago == "aprobado",
    ).first()
    if ya_pagado:
        raise HTTPException(status_code=400, detail="Este pedido ya fue pagado")

    # Calcular monto real desde los detalles del pedido
    detalles = db.query(models.DetallePedido).filter(
        models.DetallePedido.id_pedido == datos.id_pedido
    ).all()
    if not detalles:
        raise HTTPException(status_code=400, detail="El pedido no tiene productos")

    monto_real = sum(d.cantidad * d.precio_unitario for d in detalles)

    pago = models.Pago(
        id_pedido=datos.id_pedido,
        metodo_pago=datos.metodo_pago,
        estado_pago="aprobado",
        fecha_pago=datetime.utcnow(),
        monto=monto_real,
    )
    db.add(pago)
    db.commit()
    db.refresh(pago)
    return pago


@router.get("/{id_pago}", response_model=schemas.PagoResponse)
def obtener_pago(
    id_pago: int,
    db: Session = Depends(get_session),
    _=Depends(get_current_user),
):
    pago = db.query(models.Pago).filter(models.Pago.id_pago == id_pago).first()
    if not pago:
        raise HTTPException(status_code=404, detail="Pago no encontrado")
    return pago


@router.get("/pedido/{id_pedido}", response_model=schemas.PagoResponse)
def pago_por_pedido(
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

    pago = db.query(models.Pago).filter(models.Pago.id_pedido == id_pedido).first()
    if not pago:
        raise HTTPException(status_code=404, detail="Este pedido aún no tiene pago")
    return pago
