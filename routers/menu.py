from fastapi import APIRouter, HTTPException, status
from models.item_menu import ItemMenu
from database import supabase
from typing import Optional

router = APIRouter(prefix="/menu", tags=["menu"])

#   TODO: [HECHO] Hacer busquedas por nombre
#       : Hacer Soft Delete del item del menu (revisar tabla plato) (opcional?)

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_menu_item(item: ItemMenu):
    try:
        data = supabase.table("item_menu").insert(item.model_dump(exclude_none=True)).execute()
        return data.data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/")
def get_menu_items(q: Optional[str] = None):
    try:
        if q:
            # Búsqueda ignorando mayúsculas/minúsculas
            data = (supabase.table("item_menu")
                    .select("*")
                    .ilike("nombre", f"%{q}%")
                    .execute())
            return data.data
            
        # Si no se envía el parámetro 'q', retorna todo el menú
        data = supabase.table("item_menu").select("*").execute()
        return data.data
        
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al procesar la solicitud del menú."
        )@router.get("/")
def get_menu_items(q: Optional[str] = None):
    try:
        if q:
            # Búsqueda ignorando mayúsculas/minúsculas
            data = (supabase.table("item_menu")
                    .select("*")
                    .ilike("nombre", f"%{q}%")
                    .execute())
            return data.data
            
        # Si no se envía el parámetro 'q', retorna todo el menú
        data = supabase.table("item_menu").select("*").execute()
        return data.data
        
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al procesar la solicitud del menú."
        )

@router.get("/{item_id}")
def get_menu_item(item_id: int):
    try:
        data = supabase.table("item_menu").select("*").eq("id", item_id).execute()
        if not data.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item de menú con id {item_id} no encontrado"
            )
        return data.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )




