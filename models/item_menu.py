from pydantic import BaseModel, Field, StringConstraints
from typing import Annotated

class ItemMenu(BaseModel):
    id: int
    nombre: Annotated[str, StringConstraints(min_length=2, max_length=100, strip_whitespace=True)]
    descripcion: Annotated[str | None, StringConstraints(strip_whitespace=True)] = None
    precio: float = Field(..., gt=0.0, description="El precio debe ser mayor a 0")
    stock_disponible: int = Field(default=0, ge=0, description="El stock no puede ser negativo")
    categoria: str | None = None