from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_session
from routes.auth import hash_password, verify_password, create_access_token, get_current_user, require_rol
import models, schemas

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


# ─── Login invitado (solo teléfono, rol cliente) ──────────────────────────────
@router.post("/login-invitado", response_model=schemas.Token)
def login_invitado(datos: schemas.LoginInvitado, db: Session = Depends(get_session)):
    """
    El cliente ingresa solo su teléfono.
    Si no existe, se crea automáticamente con rol 'cliente'.
    Se devuelve un token de sesión.
    """
    usuario = db.query(models.Usuario).filter(
        models.Usuario.telefono == datos.telefono
    ).first()

    if not usuario:
        # Registro silencioso
        usuario = models.Usuario(
            telefono=datos.telefono,
            nombre=None,
            contrasena=None,
            rol="cliente",
        )
        db.add(usuario)
        db.commit()
        db.refresh(usuario)

    # Solo clientes pueden usar este endpoint
    if usuario.rol != "cliente":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Este acceso es solo para clientes. Usa el login de restaurante.",
        )

    token = create_access_token({"sub": str(usuario.id_usuario)})
    return {"access_token": token, "token_type": "bearer", "rol": usuario.rol}


# ─── Login restaurante (teléfono + contraseña, rol restaurante) ───────────────
@router.post("/login-restaurante", response_model=schemas.Token)
def login_restaurante(datos: schemas.LoginRestauranteSchema, db: Session = Depends(get_session)):
    """
    Login exclusivo para cuentas con rol 'restaurante'.
    Requiere teléfono + contraseña.
    """
    usuario = db.query(models.Usuario).filter(
        models.Usuario.telefono == datos.telefono
    ).first()

    if not usuario or usuario.rol != "restaurante":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas o cuenta sin acceso de restaurante.",
        )

    if not usuario.contrasena or not verify_password(datos.contrasena, usuario.contrasena):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Teléfono o contraseña incorrectos.",
        )

    token = create_access_token({"sub": str(usuario.id_usuario)})
    return {"access_token": token, "token_type": "bearer", "rol": usuario.rol}


# ─── Login OAuth2 estándar (para Swagger / compatibilidad) ────────────────────
@router.post("/login", response_model=schemas.Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_session)):
    usuario = db.query(models.Usuario).filter(
        models.Usuario.telefono == form.username
    ).first()
    if not usuario or not usuario.contrasena or not verify_password(form.password, usuario.contrasena):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Teléfono o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token({"sub": str(usuario.id_usuario)})
    return {"access_token": token, "token_type": "bearer", "rol": usuario.rol}


# ─── Registro de restaurante (solo admin) ────────────────────────────────────
@router.post("/registro-restaurante", response_model=schemas.UsuarioResponse, status_code=status.HTTP_201_CREATED)
def registrar_restaurante(
    datos: schemas.UsuarioCreate,
    db: Session = Depends(get_session),
    _: models.Usuario = Depends(require_rol("admin")),
):
    """
    Solo un admin puede crear cuentas de restaurante.
    """
    existente = db.query(models.Usuario).filter(
        models.Usuario.telefono == datos.telefono
    ).first()
    if existente:
        raise HTTPException(status_code=400, detail="El teléfono ya está registrado")

    if not datos.contrasena:
        raise HTTPException(status_code=400, detail="Los restaurantes requieren contraseña")

    nuevo = models.Usuario(
        nombre=datos.nombre,
        telefono=datos.telefono,
        contrasena=hash_password(datos.contrasena),
        rol="restaurante",
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


# ─── Perfil y CRUD ────────────────────────────────────────────────────────────

@router.get("/me", response_model=schemas.UsuarioResponse)
def perfil(usuario_actual: models.Usuario = Depends(get_current_user)):
    return usuario_actual


@router.get("/", response_model=list[schemas.UsuarioResponse])
def listar(db: Session = Depends(get_session), _=Depends(require_rol("admin"))):
    return db.query(models.Usuario).all()


@router.get("/{id_usuario}", response_model=schemas.UsuarioResponse)
def obtener(id_usuario: int, db: Session = Depends(get_session), _=Depends(get_current_user)):
    usuario = db.query(models.Usuario).filter(models.Usuario.id_usuario == id_usuario).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@router.put("/{id_usuario}", response_model=schemas.UsuarioResponse)
def actualizar(
    id_usuario: int,
    datos: schemas.UsuarioCreate,
    db: Session = Depends(get_session),
    usuario_actual: models.Usuario = Depends(get_current_user),
):
    if usuario_actual.id_usuario != id_usuario:
        raise HTTPException(status_code=403, detail="No puedes editar otro usuario")
    usuario_actual.nombre = datos.nombre
    usuario_actual.telefono = datos.telefono
    db.commit()
    db.refresh(usuario_actual)
    return usuario_actual


@router.delete("/{id_usuario}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(
    id_usuario: int,
    db: Session = Depends(get_session),
    usuario_actual: models.Usuario = Depends(get_current_user),
):
    if usuario_actual.id_usuario != id_usuario:
        raise HTTPException(status_code=403, detail="No puedes eliminar otro usuario")
    db.delete(usuario_actual)
    db.commit()
