from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from database import supabase

router = APIRouter(prefix="/pedidos", tags=["pedidos"])

#   TODO: Usar Variables de memoria para actualizar plato por plato hasta completar la orden
#         (Posiblemente se use un diccionario como base de datos temporal)
#       : Imprimir pedidos por empleado (opcional?)
#       : Obtener datos del empleado mediante el id insertado en pedido
#       : Crear tabla cliente
#       : Imprimir pedidos por grupo


# Pydantic schemas for the complex JSON input
class DetallePedidoInput(BaseModel):
    item_menu_id: int
    cantidad: int
    notas: Optional[str] = None

class PedidoInput(BaseModel):
    emisor_id: Optional[int] = None
    grupo_id: Optional[int] = None
    prioridad: Optional[str] = None
    origen_pedido: Optional[str] = None
    numero_mesa: Optional[str] = None
    detalles: List[DetallePedidoInput]

class EstadoUpdateInput(BaseModel):
    estado: str

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_comanda(comanda: PedidoInput):
    try:
        # 1. Insert header data (pedido) into Supabase
        pedido_payload = {
            "emisor_id": comanda.emisor_id,
            "grupo_id": comanda.grupo_id,
            "prioridad": comanda.prioridad,
            "origen_pedido": comanda.origen_pedido,
            "numero_mesa": comanda.numero_mesa
        }
        res_pedido = supabase.table("pedido").insert(pedido_payload).execute()
        
        if not res_pedido.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo crear la cabecera del pedido."
            )
        
        pedido_id = res_pedido.data[0]["id"]
        
        # 2. Prepare and insert details list (detalle_pedido)
        detalles_payload = []
        for det in comanda.detalles:
            detalles_payload.append({
                "pedido_id": pedido_id,
                "item_menu_id": det.item_menu_id,
                "cantidad": det.cantidad,
                "notas_especificas": det.notas  # Maps input 'notas' to DB column
            })
            
        res_detalles = supabase.table("detalle_pedido").insert(detalles_payload).execute()
        
        # 3. Check and update stock for each item in the order
        for det in comanda.detalles:
            item_res = supabase.table("item_menu").select("nombre, stock_disponible").eq("id", det.item_menu_id).execute()
            if not item_res.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"El plato con ID {det.item_menu_id} no existe."
                )
            
            plato = item_res.data[0]
            stock_actual = plato["stock_disponible"]
            
            if stock_actual < det.cantidad:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"El plato '{plato['nombre']}' no tiene stock suficiente. Stock disponible: {stock_actual}, Solicitado: {det.cantidad}"
                )
            
            # Update stock in database
            nuevo_stock = stock_actual - det.cantidad
            supabase.table("item_menu").update({"stock_disponible": nuevo_stock}).eq("id", det.item_menu_id).execute()
        
        return {
            "mensaje": "Comanda creada exitosamente",
            "pedido": res_pedido.data[0],
            "detalles": res_detalles.data
        }
        
    except HTTPException:
        # Re-raise HTTPExceptions
        raise
    except Exception as e:
        # Catch any database or connection errors and raise HTTPException
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al procesar la comanda: {str(e)}"
        )

@router.get("/activos")
def get_pedidos_activos():
    try:
        res = supabase.table("pedido").select("*, detalle_pedido(*)").neq("estado_comanda", "Despachado").execute()
        return res.data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener pedidos activos: {str(e)}"
        )

@router.patch("/{pedido_id}/estado")
def update_pedido_estado(pedido_id: int, input_data: EstadoUpdateInput):
    try:
        now_str = datetime.now().isoformat()
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
