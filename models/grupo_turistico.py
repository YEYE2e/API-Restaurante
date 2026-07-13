from pydantic import BaseModel

class GrupoTuristico(BaseModel):
    id: int
    nombre_guia: str | None = None
    identificador_grupo: str
    capacidad_max: int | None = None
    agencia: str | None = None
    estado: str | None = None