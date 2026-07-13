from pydantic import BaseModel

class ItemMenu(BaseModel):
    id: int
    nombre: str
    descripcion: str | None = None
    precio: float
    stock_disponible: int = 0
    categoria: str | None = None