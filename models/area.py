from pydantic import BaseModel

class Area(BaseModel):
    id: int
    nombre: str