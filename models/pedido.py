from datetime import datetime
from pydantic import BaseModel

class Pedido(BaseModel):
    id: int
    fecha_creacion: datetime | None = None
    fecha_actualizacion: datetime | None = None
    estado_comanda: str | None = None
    prioridad: str | None = None
    origen_pedido: str | None = None
    numero_mesa: str | None = None
    emisor_id: int | None = None
    grupo_id: int | None = None

