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
    if not (1.0 <= datos.puntuacion <= 5.0):
        raise HTTPException(status_code=400, detail="La puntuación debe estar entre 1 y 5")

    restaurante = db.query(models.Restaurante).filter(
        models.Restaurante.id_restaurante == datos.id_restaurante
    ).first()
    if not restaurante:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")

    # Verificar que el usuario haya hecho al menos un pedido en ese restaurante
    pedido = db.query(models.Pedido).filter(
        models.Pedido.id_usuario == usuario_actual.id_usuario,
        models.Pedido.id_restaurante == datos.id_restaurante,
        models.Pedido.estado == 3,  # entregado
    ).first()
    if not pedido:
        raise HTTPException(
            status_code=403,
            detail="Solo puedes calificar restaurantes donde hayas hecho pedidos entregados",
        )

    ya_califico = db.query(models.Calificacion).filter(
        models.Calificacion.id_usuario == usuario_actual.id_usuario,
        models.Calificacion.id_restaurante == datos.id_restaurante,
    ).first()
    if ya_califico:
        raise HTTPException(status_code=400, detail="Ya calificaste este restaurante")

    calificacion = models.Calificacion(
        id_usuario=usuario_actual.id_usuario,
        id_restaurante=datos.id_restaurante,
        puntuacion=datos.puntuacion,
        comentarios=datos.comentarios,
        fecha=datetime.utcnow(),
    )
    db.add(calificacion)

    # Recalcular promedio del restaurante
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
    restaurante = db.query(models.Restaurante).filter(
        models.Restaurante.id_restaurante == id_restaurante
    ).first()
    if not restaurante:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")
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


@router.delete("/{id_calificacion}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_calificacion(
    id_calificacion: int,
    db: Session = Depends(get_session),
    usuario_actual: models.Usuario = Depends(get_current_user),
):
    cal = db.query(models.Calificacion).filter(
        models.Calificacion.id_calificacion == id_calificacion,
        models.Calificacion.id_usuario == usuario_actual.id_usuario,
    ).first()
    if not cal:
        raise HTTPException(status_code=404, detail="Calificación no encontrada")

    # Recalcular promedio al eliminar
    restaurante = db.query(models.Restaurante).filter(
        models.Restaurante.id_restaurante == cal.id_restaurante
    ).first()
    todas = db.query(models.Calificacion).filter(
        models.Calificacion.id_restaurante == cal.id_restaurante,
        models.Calificacion.id_calificacion != id_calificacion,
    ).all()
    restaurante.calificacion_promedio = (
        round(sum(c.puntuacion for c in todas) / len(todas), 2) if todas else 0.0
    )

    db.delete(cal)
    db.commit()
