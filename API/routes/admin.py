from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_session
import models, schemas
from routes.auth import get_current_user, require_rol

router = APIRouter(prefix="/admin", tags=["Administrador"])


# ─── Todos los restaurantes ───────────────────────────────────────────────────

@router.get("/restaurantes", response_model=list[schemas.RestauranteAdmin])
def listar_todos_restaurantes(
    db: Session = Depends(get_session),
    _=Depends(require_rol("root")),
):
    """Devuelve todos los restaurantes sin filtrar por estado."""
    return db.query(models.Restaurante).order_by(models.Restaurante.id_restaurante.desc()).all()


# ─── Solicitudes pendientes ───────────────────────────────────────────────────

@router.get("/solicitudes", response_model=list[schemas.RestauranteAdmin])
def listar_solicitudes(
    db: Session = Depends(get_session),
    _=Depends(require_rol("root")),
):
    """Restaurantes que esperan activación."""
    return db.query(models.Restaurante).filter(
        models.Restaurante.estado == False
    ).order_by(models.Restaurante.id_restaurante.desc()).all()


# ─── Activar restaurante ──────────────────────────────────────────────────────

@router.patch("/restaurantes/{id_restaurante}/activar", response_model=schemas.RestauranteAdmin)
def activar_restaurante(
    id_restaurante: int,
    db: Session = Depends(get_session),
    _=Depends(require_rol("root")),
):
    r = db.query(models.Restaurante).filter(
        models.Restaurante.id_restaurante == id_restaurante
    ).first()
    if not r:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")
    r.estado = True
    db.commit()
    db.refresh(r)
    return r


# ─── Desactivar restaurante ───────────────────────────────────────────────────

@router.patch("/restaurantes/{id_restaurante}/desactivar", response_model=schemas.RestauranteAdmin)
def desactivar_restaurante(
    id_restaurante: int,
    db: Session = Depends(get_session),
    _=Depends(require_rol("root")),
):
    r = db.query(models.Restaurante).filter(
        models.Restaurante.id_restaurante == id_restaurante
    ).first()
    if not r:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")
    r.estado = False
    db.commit()
    db.refresh(r)
    return r
