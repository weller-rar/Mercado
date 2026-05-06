from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_session
import models, schemas
from routes.auth import hash_password, verify_password, create_access_token, get_current_restaurante, require_rol

router = APIRouter(tags=["Restaurantes"])


# ─── Login ────────────────────────────────────────────────────────────────────

@router.post("/restaurantes/login", response_model=schemas.TokenRestaurante)
def login_restaurante(datos: schemas.LoginRestauranteSchema, db: Session = Depends(get_session)):
    restaurante = db.query(models.Restaurante).filter(
        models.Restaurante.id_comercial == datos.id_comercial).first()
    if not restaurante or not verify_password(datos.contrasena, restaurante.contrasena):
        raise HTTPException(status_code=401, detail="ID comercial o contraseña incorrectos.")
    if not restaurante.estado:
        raise HTTPException(status_code=403, detail="Tu restaurante aún no ha sido activado. Contacta al administrador del parque.")
    token = create_access_token({"sub": str(restaurante.id_restaurante), "tipo": "restaurante"})
    return {"access_token": token, "token_type": "bearer",
            "id_restaurante": restaurante.id_restaurante,
            "id_comercial": restaurante.id_comercial, "nombre": restaurante.nombre}


# ─── Registro solicitud ───────────────────────────────────────────────────────

@router.post("/restaurantes/registro", response_model=schemas.RestaurantePublico, status_code=201)
def registrar_restaurante(datos: schemas.RestauranteCreate, db: Session = Depends(get_session)):
    if db.query(models.Restaurante).filter(models.Restaurante.id_comercial == datos.id_comercial).first():
        raise HTTPException(status_code=400, detail="Ese ID comercial ya está en uso. Elige otro.")
    nuevo = models.Restaurante(
        id_comercial=datos.id_comercial, nombre=datos.nombre,
        descripcion=datos.descripcion, horario=datos.horario,
        contrasena=hash_password(datos.contrasena), estado=False)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


# ─── Activar (solo admin) ─────────────────────────────────────────────────────

@router.patch("/restaurantes/{id_restaurante}/activar", response_model=schemas.RestauranteResponse)
def activar_restaurante(id_restaurante: int, db: Session = Depends(get_session), _=Depends(require_rol("admin"))):
    r = db.query(models.Restaurante).filter(models.Restaurante.id_restaurante == id_restaurante).first()
    if not r:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")
    r.estado = True
    db.commit()
    db.refresh(r)
    return r


# ─── Listar restaurantes públicos ─────────────────────────────────────────────

@router.get("/restaurantes", response_model=list[schemas.RestaurantePublico])
def listar_restaurantes(db: Session = Depends(get_session)):
    return db.query(models.Restaurante).filter(models.Restaurante.estado == True).all()

@router.get("/restaurantes/{id_comercial}", response_model=schemas.RestaurantePublico)
def obtener_restaurante(id_comercial: str, db: Session = Depends(get_session)):
    r = db.query(models.Restaurante).filter(
        models.Restaurante.id_comercial == id_comercial,
        models.Restaurante.estado == True).first()
    if not r:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")
    return r


# ─── Dashboard: perfil propio ─────────────────────────────────────────────────

@router.get("/restaurantes/me/perfil", response_model=schemas.RestauranteResponse)
def mi_perfil(restaurante_actual: models.Restaurante = Depends(get_current_restaurante)):
    return restaurante_actual

@router.put("/restaurantes/me/info", response_model=schemas.RestauranteResponse)
def actualizar_info_basica(
    datos: schemas.ActualizarInfoBasica,
    db: Session = Depends(get_session),
    restaurante_actual: models.Restaurante = Depends(get_current_restaurante),
):
    """Descripción y horario — no requiere re-auth."""
    restaurante_actual.descripcion = datos.descripcion
    restaurante_actual.horario = datos.horario
    db.commit()
    db.refresh(restaurante_actual)
    return restaurante_actual

@router.put("/restaurantes/me/nombre", response_model=schemas.RestauranteResponse)
def actualizar_nombre(
    datos: schemas.ActualizarNombreSchema,
    db: Session = Depends(get_session),
    restaurante_actual: models.Restaurante = Depends(get_current_restaurante),
):
    """Cambiar nombre requiere confirmar id_comercial + contraseña."""
    if datos.id_comercial != restaurante_actual.id_comercial:
        raise HTTPException(status_code=401, detail="ID comercial incorrecto.")
    if not verify_password(datos.contrasena, restaurante_actual.contrasena):
        raise HTTPException(status_code=401, detail="Contraseña incorrecta.")
    restaurante_actual.nombre = datos.nombre
    db.commit()
    db.refresh(restaurante_actual)
    return restaurante_actual


# ─── Dashboard: Menús ─────────────────────────────────────────────────────────

@router.get("/restaurantes/me/menus", response_model=list[schemas.MenuResponse])
def mis_menus(db: Session = Depends(get_session),
              restaurante_actual: models.Restaurante = Depends(get_current_restaurante)):
    return db.query(models.Menu).filter(
        models.Menu.id_restaurante == restaurante_actual.id_restaurante).all()

@router.get("/restaurantes/{id_comercial}/menus", response_model=list[schemas.MenuResponse])
def listar_menus_publico(id_comercial: str, db: Session = Depends(get_session)):
    r = db.query(models.Restaurante).filter(models.Restaurante.id_comercial == id_comercial).first()
    if not r:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")
    return db.query(models.Menu).filter(models.Menu.id_restaurante == r.id_restaurante).all()

@router.post("/menus", response_model=schemas.MenuResponse, status_code=201)
def crear_menu(datos: schemas.MenuCreate, db: Session = Depends(get_session),
               restaurante_actual: models.Restaurante = Depends(get_current_restaurante)):
    if datos.id_restaurante != restaurante_actual.id_restaurante:
        raise HTTPException(status_code=403, detail="No puedes crear menús en otro restaurante.")
    nuevo = models.Menu(**datos.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.delete("/menus/{id_menu}", status_code=204)
def eliminar_menu(id_menu: int, db: Session = Depends(get_session),
                  restaurante_actual: models.Restaurante = Depends(get_current_restaurante)):
    m = db.query(models.Menu).filter(
        models.Menu.id_menu == id_menu,
        models.Menu.id_restaurante == restaurante_actual.id_restaurante).first()
    if not m:
        raise HTTPException(status_code=404, detail="Menú no encontrado")
    db.delete(m)
    db.commit()


# ─── Dashboard: Productos ─────────────────────────────────────────────────────

@router.get("/menus/{id_menu}/productos", response_model=list[schemas.ProductoResponse])
def listar_productos(id_menu: int, db: Session = Depends(get_session)):
    return db.query(models.Producto).filter(models.Producto.id_menu == id_menu).all()

@router.post("/productos", response_model=schemas.ProductoResponse, status_code=201)
def crear_producto(datos: schemas.ProductoCreate, db: Session = Depends(get_session),
                   restaurante_actual: models.Restaurante = Depends(get_current_restaurante)):
    menu = db.query(models.Menu).filter(
        models.Menu.id_menu == datos.id_menu,
        models.Menu.id_restaurante == restaurante_actual.id_restaurante).first()
    if not menu:
        raise HTTPException(status_code=404, detail="Menú no encontrado o no te pertenece.")
    nuevo = models.Producto(**datos.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.put("/productos/{id_producto}", response_model=schemas.ProductoResponse)
def actualizar_producto(id_producto: int, datos: schemas.ProductoCreate,
                        db: Session = Depends(get_session),
                        restaurante_actual: models.Restaurante = Depends(get_current_restaurante)):
    p = db.query(models.Producto).filter(models.Producto.id_producto == id_producto).first()
    if not p:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    for campo, valor in datos.model_dump().items():
        setattr(p, campo, valor)
    db.commit()
    db.refresh(p)
    return p

@router.patch("/productos/{id_producto}/disponibilidad", response_model=schemas.ProductoResponse)
def toggle_disponibilidad(id_producto: int, datos: schemas.ToggleDisponibilidad,
                          db: Session = Depends(get_session),
                          restaurante_actual: models.Restaurante = Depends(get_current_restaurante)):
    p = db.query(models.Producto).filter(models.Producto.id_producto == id_producto).first()
    if not p:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    p.disponible = 1 if datos.disponible else 0
    db.commit()
    db.refresh(p)
    return p

@router.delete("/productos/{id_producto}", status_code=204)
def eliminar_producto(id_producto: int, db: Session = Depends(get_session),
                      restaurante_actual: models.Restaurante = Depends(get_current_restaurante)):
    p = db.query(models.Producto).filter(models.Producto.id_producto == id_producto).first()
    if not p:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    db.delete(p)
    db.commit()
