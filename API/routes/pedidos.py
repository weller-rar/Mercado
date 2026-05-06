from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from datetime import datetime
from database import get_session
import models, schemas
from routes.auth import get_current_user, get_current_restaurante

router = APIRouter(tags=["Pedidos"])

ESTADOS = {
    1: "Pendiente de pago",
    2: "En preparación",
    3: "Listo para recoger",
    4: "Entregado",
    5: "Cancelado",
}


def _build_pedido_response(pedido: models.Pedido) -> dict:
    detalles = []
    total = 0.0
    for d in pedido.detalles:
        subtotal = d.cantidad * d.precio_unitario
        total += subtotal
        detalles.append({
            "id_detalle": d.id_detalle,
            "id_producto": d.id_producto,
            "cantidad": d.cantidad,
            "precio_unitario": d.precio_unitario,
            "nombre_producto": d.producto.nombre if d.producto else None,
            "imagen_producto": d.producto.imagen_url if d.producto else None,
        })
    return {
        "id_pedido": pedido.id_pedido,
        "id_restaurante": pedido.id_restaurante,
        "nombre_restaurante": pedido.restaurante.nombre if pedido.restaurante else None,
        "numero_orden": pedido.numero_orden,
        "fecha": pedido.fecha,
        "estado": pedido.estado,
        "metodo_pago": pedido.transaccion.metodo_pago if pedido.transaccion else None,
        "detalles": detalles,
        "total": total,
    }


# ─── CHECKOUT ─────────────────────────────────────────────────────────────────

@router.post("/checkout", response_model=schemas.TransaccionResponse, status_code=201)
def checkout(
    datos: schemas.CheckoutRequest,
    db: Session = Depends(get_session),
    usuario_actual: models.Usuario = Depends(get_current_user),
):
    """
    Recibe el carrito completo. Agrupa por restaurante y crea un pedido por cada uno.
    metodo_pago efectivo → estado 1 (pendiente pago)
    cualquier otro       → estado 2 (en preparación)
    """
    if not datos.items:
        raise HTTPException(status_code=400, detail="El carrito está vacío.")

    METODOS_VALIDOS = {"efectivo", "nequi", "tarjeta", "daviplata", "transferencia"}
    if datos.metodo_pago not in METODOS_VALIDOS:
        raise HTTPException(status_code=400, detail=f"Método de pago inválido: {datos.metodo_pago}")

    # Cargar productos
    ids = [i.id_producto for i in datos.items]
    productos = {p.id_producto: p for p in db.query(models.Producto).filter(
        models.Producto.id_producto.in_(ids)
    ).all()}

    for item in datos.items:
        if item.id_producto not in productos:
            raise HTTPException(status_code=404, detail=f"Producto {item.id_producto} no encontrado.")
        if not productos[item.id_producto].disponible:
            raise HTTPException(status_code=400, detail=f"'{productos[item.id_producto].nombre}' no está disponible.")

    # Agrupar items por restaurante (a través del menú)
    grupos: dict[int, list] = {}
    for item in datos.items:
        p = productos[item.id_producto]
        menu = db.query(models.Menu).filter(models.Menu.id_menu == p.id_menu).first()
        id_rest = menu.id_restaurante
        if id_rest not in grupos:
            grupos[id_rest] = []
        grupos[id_rest].append(item)

    # Calcular total
    total_global = sum(
        productos[i.id_producto].precio * i.cantidad
        for i in datos.items
    )

    # Estado inicial según método de pago
    estado_inicial = 1 if datos.metodo_pago == "efectivo" else 2

    # Crear transacción
    transaccion = models.Transaccion(
        id_usuario=usuario_actual.id_usuario,
        metodo_pago=datos.metodo_pago,
        total=total_global,
    )
    db.add(transaccion)
    db.flush()  # obtener id_transaccion

    pedidos_creados = []

    for id_restaurante, items_rest in grupos.items():
        pedido = models.Pedido(
            id_usuario=usuario_actual.id_usuario,
            id_restaurante=id_restaurante,
            id_transaccion=transaccion.id_transaccion,
            estado=estado_inicial,
            fecha=datetime.utcnow(),
        )
        db.add(pedido)
        db.flush()

        # Número de orden legible
        pedido.numero_orden = f"ORD-{pedido.id_pedido:04d}"

        for item in items_rest:
            detalle = models.DetallePedido(
                id_pedido=pedido.id_pedido,
                id_producto=item.id_producto,
                cantidad=item.cantidad,
                precio_unitario=productos[item.id_producto].precio,
            )
            db.add(detalle)

        pedidos_creados.append(pedido)

    db.commit()

    # Recargar con relaciones
    transaccion = db.query(models.Transaccion).options(
        joinedload(models.Transaccion.pedidos)
        .joinedload(models.Pedido.detalles)
        .joinedload(models.DetallePedido.producto),
        joinedload(models.Transaccion.pedidos)
        .joinedload(models.Pedido.restaurante),
        joinedload(models.Transaccion.pedidos)
        .joinedload(models.Pedido.transaccion),
    ).filter(models.Transaccion.id_transaccion == transaccion.id_transaccion).first()

    return {
        "id_transaccion": transaccion.id_transaccion,
        "fecha": transaccion.fecha,
        "metodo_pago": transaccion.metodo_pago,
        "total": transaccion.total,
        "pedidos": [_build_pedido_response(p) for p in transaccion.pedidos],
    }


# ─── CLIENTE: mis pedidos ─────────────────────────────────────────────────────

@router.get("/mis-pedidos", response_model=list[schemas.PedidoResponse])
def mis_pedidos(
    db: Session = Depends(get_session),
    usuario_actual: models.Usuario = Depends(get_current_user),
):
    pedidos = db.query(models.Pedido).options(
        joinedload(models.Pedido.detalles).joinedload(models.DetallePedido.producto),
        joinedload(models.Pedido.restaurante),
        joinedload(models.Pedido.transaccion),
    ).filter(
        models.Pedido.id_usuario == usuario_actual.id_usuario
    ).order_by(models.Pedido.fecha.desc()).limit(20).all()

    return [_build_pedido_response(p) for p in pedidos]


@router.get("/pedido/{id_pedido}", response_model=schemas.PedidoResponse)
def ver_pedido(
    id_pedido: int,
    db: Session = Depends(get_session),
    usuario_actual: models.Usuario = Depends(get_current_user),
):
    pedido = db.query(models.Pedido).options(
        joinedload(models.Pedido.detalles).joinedload(models.DetallePedido.producto),
        joinedload(models.Pedido.restaurante),
        joinedload(models.Pedido.transaccion),
    ).filter(
        models.Pedido.id_pedido == id_pedido,
        models.Pedido.id_usuario == usuario_actual.id_usuario,
    ).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado.")
    return _build_pedido_response(pedido)


# ─── RESTAURANTE: pedidos activos (polling) ───────────────────────────────────

@router.get("/restaurante/pedidos-activos")
def pedidos_activos(
    db: Session = Depends(get_session),
    restaurante_actual: models.Restaurante = Depends(get_current_restaurante),
):
    """Devuelve pedidos en estados 1 y 2 (pendiente pago + en preparación)."""
    pedidos = db.query(models.Pedido).options(
        joinedload(models.Pedido.detalles).joinedload(models.DetallePedido.producto),
        joinedload(models.Pedido.transaccion),
    ).filter(
        models.Pedido.id_restaurante == restaurante_actual.id_restaurante,
        models.Pedido.estado.in_([1, 2]),
    ).order_by(models.Pedido.fecha.asc()).all()

    return [_build_pedido_response(p) for p in pedidos]


@router.get("/restaurante/historial")
def historial_ventas(
    db: Session = Depends(get_session),
    restaurante_actual: models.Restaurante = Depends(get_current_restaurante),
):
    """Devuelve pedidos entregados y cancelados para el historial."""
    pedidos = db.query(models.Pedido).options(
        joinedload(models.Pedido.detalles).joinedload(models.DetallePedido.producto),
        joinedload(models.Pedido.transaccion),
    ).filter(
        models.Pedido.id_restaurante == restaurante_actual.id_restaurante,
        models.Pedido.estado.in_([3, 4, 5]),
    ).order_by(models.Pedido.fecha.desc()).limit(100).all()

    return [_build_pedido_response(p) for p in pedidos]


@router.get("/restaurante/verificar/{numero_orden}")
def verificar_pedido(
    numero_orden: str,
    db: Session = Depends(get_session),
    restaurante_actual: models.Restaurante = Depends(get_current_restaurante),
):
    """Verifica un pedido por número de orden (para el cajero)."""
    pedido = db.query(models.Pedido).options(
        joinedload(models.Pedido.detalles).joinedload(models.DetallePedido.producto),
        joinedload(models.Pedido.transaccion),
        joinedload(models.Pedido.usuario),
    ).filter(
        models.Pedido.numero_orden == numero_orden.upper(),
        models.Pedido.id_restaurante == restaurante_actual.id_restaurante,
    ).first()

    if not pedido:
        raise HTTPException(status_code=404, detail="Número de orden no encontrado en este restaurante.")

    result = _build_pedido_response(pedido)
    result["telefono_cliente"] = pedido.usuario.telefono if pedido.usuario else None
    return result


@router.patch("/restaurante/pedido/{id_pedido}/estado")
def actualizar_estado(
    id_pedido: int,
    datos: schemas.ActualizarEstado,
    db: Session = Depends(get_session),
    restaurante_actual: models.Restaurante = Depends(get_current_restaurante),
):
    if datos.estado not in ESTADOS:
        raise HTTPException(status_code=400, detail=f"Estado inválido. Opciones: {ESTADOS}")

    pedido = db.query(models.Pedido).filter(
        models.Pedido.id_pedido == id_pedido,
        models.Pedido.id_restaurante == restaurante_actual.id_restaurante,
    ).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado.")

    pedido.estado = datos.estado
    db.commit()
    return {"ok": True, "estado": datos.estado, "estado_texto": ESTADOS[datos.estado]}
