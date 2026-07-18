from fastapi import APIRouter, Form, HTTPException, status
from postgrest.exceptions import APIError
from typing import Annotated
from models.area import Area
from models.empleado import Empleado
from datetime import datetime, timezone
from database import supabase


#   TODO: Imprimir empleados filtrados por area cuyo estado de empleado sea True.
#       : Imprimir todos los empleados (opcional)
#       : Cambiar forma de login (opcional?)
#       : Cambiar permisos para eliminar usuario (Revisar documento Seguridad)



router = APIRouter()

@router.post("/area/")
def create_area(area: Area):
    data = supabase.table("area").insert({
        "nombre": area.nombre
    }).execute()
    return data.data


@router.post("/empleado/")
def create_user(area_busqueda: int, empleado: Empleado):
    area = (supabase.table("area")
            .select("*")
            .ilike("id", f"%{area_busqueda}%").
            execute())
    if area:
        area_id = area.data[0]["id"]
    else:    
        raise HTTPException(
            status_code=404, 
            detail=f"El área '{area_busqueda}' no existe en el sistema."
        )

    data = supabase.table("empleado").insert({
        "area_id": area_id,
        "nombre": empleado.nombre,
        "pin_acceso": empleado.pin_acceso,
        "cargo": empleado.cargo,
        "estado": empleado.estado
    }).execute()
    return data.data
    

@router.post("/empleado/login")
def login(nombre: Annotated[str, Form()], pin: Annotated[int, Form()]):
    try:
        # Excluimos el pin_acceso en el select por seguridad
        data = (supabase.table("empleado")
                .select("id, nombre, cargo, estado, area_id") 
                .eq("nombre", nombre)
                .eq("pin_acceso", pin)
                .execute())

        if not data.data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Credenciales incorrectas."
            )
            
        usuario = data.data[0]
        if not usuario["estado"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="El usuario no se encuentra activo."
            )
            
        return usuario
        
    except HTTPException:
        raise
    except Exception:
        # Error genérico 500 sin exponer detalles de la base de datos
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno de autenticación."
        )

@router.patch("/empleado/delete/")
def delete_user(id: int):
    mensaje = ""
    now_str = datetime.now(timezone.utc).isoformat()
    try:
        data = (supabase.table("empleado")
                .update({"estado": False,
                        "fecha_salida": now_str})
                .eq("id", id)
                .execute())
        mensaje = "Éxito:", data.data
    except APIError as e:
        mensaje = "Error de Supabase:", e.message
    return mensaje