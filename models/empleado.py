from pydantic import BaseModel
from datetime import datetime

class Empleado(BaseModel):
    id: int
    area_id: int | None = None
    nombre: str
    pin_acceso: int | None = None
    cargo: str | None = None
    fecha_entrada: datetime | None = None
    fecha_salida: datetime | None = None
    estado: bool = True

