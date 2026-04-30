from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_session
import models, schemas
from routes.auth import get_current_user

router = APIRouter(tags=["Restaurantes"])


# ─── Restaurantes ─────────────────────────────────────────────────────────────

@router.get("/restaurantes", response_model=list[schemas.RestauranteResponse])
def listar_restaurantes(db: Session = Depends(get_session)):
    return db.query(models.Restaurante).all()


@router.get("/restaurantes/{id_restaurante}", response_model=schemas.RestauranteResponse)
def obtener_restaurante(id_restaurante: int, db: Session = Depends(get_session)):
    r = db.query(models.Restaurante).filter(
        models.Restaurante.id_restaurante == id_restaurante
    ).first()
    if not r:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")
    return r


@router.post("/restaurantes", response_model=schemas.RestauranteResponse, status_code=status.HTTP_201_CREATED)
def crear_restaurante(
    datos: schemas.RestauranteCreate,
    db: Session = Depends(get_session),
    _=Depends(get_current_user),
):
    nuevo = models.Restaurante(**datos.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.put("/restaurantes/{id_restaurante}", response_model=schemas.RestauranteResponse)
def actualizar_restaurante(
    id_restaurante: int,
    datos: schemas.RestauranteCreate,
    db: Session = Depends(get_session),
    _=Depends(get_current_user),
):
    r = db.query(models.Restaurante).filter(
        models.Restaurante.id_restaurante == id_restaurante
    ).first()
    if not r:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")
    for campo, valor in datos.model_dump().items():
        setattr(r, campo, valor)
    db.commit()
    db.refresh(r)
    return r


@router.delete("/restaurantes/{id_restaurante}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_restaurante(
    id_restaurante: int,
    db: Session = Depends(get_session),
    _=Depends(get_current_user),
):
    r = db.query(models.Restaurante).filter(
        models.Restaurante.id_restaurante == id_restaurante
    ).first()
    if not r:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")
    db.delete(r)
    db.commit()


# ─── Menús ────────────────────────────────────────────────────────────────────

@router.get("/restaurantes/{id_restaurante}/menus", response_model=list[schemas.MenuResponse])
def listar_menus(id_restaurante: int, db: Session = Depends(get_session)):
    return db.query(models.Menu).filter(
        models.Menu.id_restaurante == id_restaurante
    ).all()


@router.get("/menus/{id_menu}", response_model=schemas.MenuResponse)
def obtener_menu(id_menu: int, db: Session = Depends(get_session)):
    m = db.query(models.Menu).filter(models.Menu.id_menu == id_menu).first()
    if not m:
        raise HTTPException(status_code=404, detail="Menú no encontrado")
    return m


@router.post("/menus", response_model=schemas.MenuResponse, status_code=status.HTTP_201_CREATED)
def crear_menu(
    datos: schemas.MenuCreate,
    db: Session = Depends(get_session),
    _=Depends(get_current_user),
):
    restaurante = db.query(models.Restaurante).filter(
        models.Restaurante.id_restaurante == datos.id_restaurante
    ).first()
    if not restaurante:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")
    nuevo = models.Menu(**datos.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.delete("/menus/{id_menu}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_menu(
    id_menu: int,
    db: Session = Depends(get_session),
    _=Depends(get_current_user),
):
    m = db.query(models.Menu).filter(models.Menu.id_menu == id_menu).first()
    if not m:
        raise HTTPException(status_code=404, detail="Menú no encontrado")
    db.delete(m)
    db.commit()


# ─── Productos ────────────────────────────────────────────────────────────────

@router.get("/menus/{id_menu}/productos", response_model=list[schemas.ProductoResponse])
def listar_productos(id_menu: int, db: Session = Depends(get_session)):
    return db.query(models.Producto).filter(models.Producto.id_menu == id_menu).all()


@router.get("/productos/{id_producto}", response_model=schemas.ProductoResponse)
def obtener_producto(id_producto: int, db: Session = Depends(get_session)):
    p = db.query(models.Producto).filter(models.Producto.id_producto == id_producto).first()
    if not p:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return p


@router.post("/productos", response_model=schemas.ProductoResponse, status_code=status.HTTP_201_CREATED)
def crear_producto(
    datos: schemas.ProductoCreate,
    db: Session = Depends(get_session),
    _=Depends(get_current_user),
):
    menu = db.query(models.Menu).filter(models.Menu.id_menu == datos.id_menu).first()
    if not menu:
        raise HTTPException(status_code=404, detail="Menú no encontrado")
    nuevo = models.Producto(**datos.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.put("/productos/{id_producto}", response_model=schemas.ProductoResponse)
def actualizar_producto(
    id_producto: int,
    datos: schemas.ProductoCreate,
    db: Session = Depends(get_session),
    _=Depends(get_current_user),
):
    p = db.query(models.Producto).filter(models.Producto.id_producto == id_producto).first()
    if not p:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    for campo, valor in datos.model_dump().items():
        setattr(p, campo, valor)
    db.commit()
    db.refresh(p)
    return p


@router.delete("/productos/{id_producto}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_producto(
    id_producto: int,
    db: Session = Depends(get_session),
    _=Depends(get_current_user),
):
    p = db.query(models.Producto).filter(models.Producto.id_producto == id_producto).first()
    if not p:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    db.delete(p)
    db.commit()
