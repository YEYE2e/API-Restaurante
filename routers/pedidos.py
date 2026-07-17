from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, StringConstraints
from typing import List, Optional, Annotated
from datetime import datetime, timezone
from database import supabase

router = APIRouter(prefix="/pedidos", tags=["pedidos"])

#   TODO: Imprimir pedidos por empleado (opcional?)
#       : [HECHO] Obtener datos del empleado mediante el id insertado en pedido
#       : [HECHO] Filtrar pedidos a despachar por grupo
#       : Implementar asyncio (o talvez no por la atomicidad de postgresql)

# Pydantic schemas for the complex JSON input
class DetallePedidoInput(BaseModel):
    item_menu_id: int = Field(..., gt=0)
    cantidad: int = Field(..., gt=0, description="La cantidad solicitada debe ser de al menos 1")
    notas: Annotated[str | None, StringConstraints(strip_whitespace=True)] = None

class PedidoInput(BaseModel):
    emisor_id: Optional[int] = None
    grupo_id: Optional[int] = None
    prioridad: Optional[str] = None
    origen_pedido: Optional[str] = None
    numero_mesa: Optional[str] = None
    nombre_referencia: Annotated[str | None, StringConstraints(strip_whitespace=True)] = None
    detalles: List[DetallePedidoInput]

class EstadoUpdateInput(BaseModel):
    estado: str

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_comanda(comanda: PedidoInput):
    try:
        detalles_json = [
            {
                "item_menu_id": d.item_menu_id,
                "cantidad": d.cantidad,
                "notas": d.notas
            }
            for d in comanda.detalles
        ]
        
        params = {
            "p_emisor_id": comanda.emisor_id,
            "p_grupo_id": comanda.grupo_id,
            "p_prioridad": comanda.prioridad,
            "p_origen_pedido": comanda.origen_pedido,
            "p_numero_mesa": comanda.numero_mesa,
            "p_nombre_referencia": comanda.nombre_referencia,
            "p_detalles": detalles_json
        }
        
        res = supabase.rpc("crear_pedido_con_stock", params).execute()
        return res.data
        
    except Exception as e:
        error_text = getattr(e, "message", str(e))
        if "no existe" in error_text or "stock suficiente" in error_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_text
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor."
        )

# Q: deberiamos agregar mas estado con neq? posiblemente si
@router.get("/activos")
def get_pedidos_activos():
    try:
        query = "*, empleado:emisor_id(nombre), detalle_pedido(*, item_menu:item_menu_id(nombre))"
        res = supabase.table("pedido").select(query).neq("estado_comanda", "Despachado").execute()
        return res.data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener pedidos activos: {str(e)}"
        )
    
@router.get("/activos/{grupo_id}")
def get_pedidos_grupo_activos(grupo_id: int):
    try:
        res = (supabase.table("pedido")
               .select("*, detalle_pedido(*)")
               .eq("grupo_id", grupo_id)
               .neq("estado_comanda", "Despachado")
               .execute())
        return res.data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener pedidos activos: {str(e)}"
        )

@router.patch("/{pedido_id}/estado")
def update_pedido_estado(pedido_id: int, input_data: EstadoUpdateInput):
    try:
        now_str = datetime.now(timezone.utc).isoformat()
        res = supabase.table("pedido").update({
            "estado_comanda": input_data.estado,
            "fecha_actualizacion": now_str
        }).eq("id", pedido_id).execute()
        
        if not res.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pedido con id {pedido_id} no encontrado."
            )
        return res.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al actualizar el estado del pedido: {str(e)}"
        )

@router.get("/{pedido_id}/{user_id}")
def get_user_pedido(pedido_id: int):
    try:
        data = (supabase.table("pedido")
                .select("empleado(nombre, id)")
                .eq("id",pedido_id)
                .execute())
        if not data.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pedido con id {pedido_id} no encontrado."
            )
        return data.data[0]["empleado"]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al actualizar el estado del pedido: {str(e)}"
        )