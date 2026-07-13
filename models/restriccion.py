from pydantic import BaseModel

class Restriccion(BaseModel):
    id: int
    tipo: str

