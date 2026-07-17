from pydantic import BaseModel, Field, StringConstraints
from typing import Annotated
from datetime import datetime

class Empleado(BaseModel):
    id: int
    area_id: int | None = None
    nombre: Annotated[str, StringConstraints(min_length=2, max_length=100, strip_whitespace=True)]
    pin_acceso: int = Field(..., ge=1000, le=999999, description="PIN numérico de 4 a 6 dígitos")
    cargo: str | None = None
    fecha_entrada: datetime | None = None
    fecha_salida: datetime | None = None
    estado: bool = True

