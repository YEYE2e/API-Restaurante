from pydantic import BaseModel

class Area(BaseModel):
    id: int | None = None
    nombre: str