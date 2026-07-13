from pydantic import BaseModel

class ItemRestriccion(BaseModel):
    item_menu_id: int
    restriccion_id: int
    nivel_gravedad: str | None = None