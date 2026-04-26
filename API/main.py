from fastapi import FastAPI
from pydantic import BaseModel

class ItemOut(BaseModel):
    name: str
    price: float
    tax: float | None = None

class ItemIn(ItemOut):
    internal_code: str

products = {
    "a1": {
        "name": "Laptop",
        "price": 1000,
        "internal_code": "XYZ123"
    },
    "b2": {
        "name": "Mouse",
        "price": 50,
        "tax": 5,
        "internal_code": "ABC999"
    }
}

app = FastAPI()

producto = 1;

@app.get("/items/{item_id}",response_model=ItemOut,response_model_exclude_unset=True)
async def pedir(item_id:str):
    if item_id not in products:
        return {"mensaje":"No existe el producto"}
    return products[item_id]

@app.post("/items/",response_model=ItemOut,response_model_exclude_unset=True)
async def crear(item:ItemIn):
    global producto
    products[str(producto)] = item.model_dump()
    producto = producto + 1
    return item