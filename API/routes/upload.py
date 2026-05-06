import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_session
from routes.auth import get_current_restaurante
import models
import os

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME", "du5tnmtio"),
    api_key=os.getenv("CLOUDINARY_API_KEY", "333357447713139"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)

router = APIRouter(tags=["Imágenes"])


@router.post("/upload/banner")
async def subir_banner(
    file: UploadFile = File(...),
    db: Session = Depends(get_session),
    restaurante_actual: models.Restaurante = Depends(get_current_restaurante),
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Solo se permiten imágenes.")
    contenido = await file.read()
    resultado = cloudinary.uploader.upload(
        contenido,
        folder="restaurantes/banners",
        public_id=f"banner_{restaurante_actual.id_comercial}",
        overwrite=True,
        transformation=[{"width": 1200, "height": 300, "crop": "fill", "quality": "auto"}],
    )
    url = resultado["secure_url"]

    # Actualizar directamente en BD por id para evitar problemas de sesión
    db.query(models.Restaurante).filter(
        models.Restaurante.id_restaurante == restaurante_actual.id_restaurante
    ).update({"imagen_url": url})
    db.commit()

    return {"url": url}


@router.post("/upload/producto/{id_producto}")
async def subir_imagen_producto(
    id_producto: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_session),
    restaurante_actual: models.Restaurante = Depends(get_current_restaurante),
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Solo se permiten imágenes.")

    # Verificar que el producto pertenece a este restaurante
    producto = db.query(models.Producto).join(models.Menu).filter(
        models.Producto.id_producto == id_producto,
        models.Menu.id_restaurante == restaurante_actual.id_restaurante,
    ).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado o no te pertenece.")

    contenido = await file.read()
    resultado = cloudinary.uploader.upload(
        contenido,
        folder="restaurantes/productos",
        public_id=f"producto_{id_producto}_{restaurante_actual.id_comercial}",
        overwrite=True,
        transformation=[{"width": 400, "height": 400, "crop": "fill", "quality": "auto"}],
    )
    url = resultado["secure_url"]

    # Actualizar directamente en BD por id
    db.query(models.Producto).filter(
        models.Producto.id_producto == id_producto
    ).update({"imagen_url": url})
    db.commit()

    return {"url": url}
