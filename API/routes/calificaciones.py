from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_session
import models, schemas
from routes.auth import get_current_user

router = APIRouter(prefix="/calificaciones", tags=["Calificaciones"])


@router.post("/", response_model=schemas.CalificacionResponse, status_code=status.HTTP_201_CREATED)
def calificar(
    datos: schemas.CalificacionCreate,
    db: Session = Depends(get_session),
    usuario_actual: models.Usuario = Depends(get_current_user),
):
    # Verificar que el restaurante existe
    restaurante = db.query(models.Restaurante).filter(
        models.Restaurante.id_restaurante == datos.id_restaurante
    ).first()
    if not restaurante:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")

    # Verificar que el usuario haya hecho al menos un pedido entregado en ese restaurante
    pedido = db.query(models.Pedido).filter(
        models.Pedido.id_usuario == usuario_actual.id_usuario,
        models.Pedido.id_restaurante == datos.id_restaurante,
        models.Pedido.estado.in_([3, 4]),  # listo o entregado
    ).first()
    if not pedido:
        raise HTTPException(
            status_code=403,
            detail="Solo puedes calificar restaurantes donde hayas hecho pedidos.",
        )

    # Verificar que no haya calificado ya
    ya_califico = db.query(models.Calificacion).filter(
        models.Calificacion.id_usuario == usuario_actual.id_usuario,
        models.Calificacion.id_restaurante == datos.id_restaurante,
    ).first()
    if ya_califico:
        raise HTTPException(status_code=400, detail="Ya calificaste este restaurante.")

    calificacion = models.Calificacion(
        id_usuario=usuario_actual.id_usuario,
        id_restaurante=datos.id_restaurante,
        puntuacion=datos.puntuacion,
        comentarios=datos.comentarios,
        fecha=datetime.utcnow(),
    )
    db.add(calificacion)

    # Recalcular promedio
    todas = db.query(models.Calificacion).filter(
        models.Calificacion.id_restaurante == datos.id_restaurante
    ).all()
    total = sum(c.puntuacion for c in todas) + datos.puntuacion
    restaurante.calificacion_promedio = round(total / (len(todas) + 1), 2)

    db.commit()
    db.refresh(calificacion)
    return calificacion


@router.get("/restaurante/{id_restaurante}", response_model=list[schemas.CalificacionResponse])
def calificaciones_restaurante(id_restaurante: int, db: Session = Depends(get_session)):
    return db.query(models.Calificacion).filter(
        models.Calificacion.id_restaurante == id_restaurante
    ).all()

@router.get("/mias", response_model=list[schemas.CalificacionResponse])
def mis_calificaciones(
    db: Session = Depends(get_session),
    usuario_actual: models.Usuario = Depends(get_current_user),
):
    return db.query(models.Calificacion).filter(
        models.Calificacion.id_usuario == usuario_actual.id_usuario
    ).all()
