from datetime import datetime, timedelta
from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import get_session
import models
import os

SECRET_KEY = os.getenv("SECRET_KEY", "cambia_esta_clave_secreta")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/usuarios/login")


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def _extract_token(request: Request) -> str | None:
    """Lee el Bearer token del header Authorization sin importar el scheme."""
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth[7:]
    return None


def get_current_user(
    request: Request,
    db: Session = Depends(get_session),
) -> models.Usuario:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = _extract_token(request)
    if not token:
        raise credentials_exception
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        tipo = payload.get("tipo", "usuario")
        if user_id is None or tipo != "usuario":
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(models.Usuario).filter(
        models.Usuario.id_usuario == int(user_id)
    ).first()
    if user is None:
        raise credentials_exception
    return user


def get_current_restaurante(
    request: Request,
    db: Session = Depends(get_session),
) -> models.Restaurante:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token de restaurante inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = _extract_token(request)
    if not token:
        raise credentials_exception
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        restaurante_id = payload.get("sub")
        tipo = payload.get("tipo")
        if restaurante_id is None or tipo != "restaurante":
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    restaurante = db.query(models.Restaurante).filter(
        models.Restaurante.id_restaurante == int(restaurante_id)
    ).first()
    if restaurante is None:
        raise credentials_exception
    if not restaurante.estado:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tu restaurante aún no ha sido activado por el administrador.",
        )
    return restaurante


def require_rol(*roles: str):
    def dependency(
        request: Request,
        db: Session = Depends(get_session),
    ):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
        token = _extract_token(request)
        if not token:
            raise credentials_exception
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
            tipo = payload.get("tipo", "usuario")
            if user_id is None or tipo != "usuario":
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        usuario = db.query(models.Usuario).filter(
            models.Usuario.id_usuario == int(user_id)
        ).first()
        if not usuario:
            raise credentials_exception
        if usuario.rol not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado. Se requiere rol: {', '.join(roles)}",
            )
        return usuario
    return dependency
