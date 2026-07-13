from pydantic import BaseModel

class DetallePedido(BaseModel):
    id: int
    pedido_id: int
    item_menu_id: int
    cantidad: int
    notas_especificas: str | None = None
