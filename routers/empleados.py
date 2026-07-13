from fastapi import APIRouter, Form, HTTPException, status
from typing import Annotated
from models.area import Area
from models.empleado import Empleado
from database import supabase

router = APIRouter()

@router.post("/area/")
def create_area(area: Area):
    data = supabase.table("area").insert({
        "nombre": area.nombre
    }).execute()
    return data.data


@router.post("/empleado/")
def create_user(area_busqueda: str, empleado: Empleado):
    area = (supabase.table("area")
            .select("*")
            .ilike("nombre", f"%{area_busqueda}%").
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
def login(nombre: Annotated[str, Form()],
          pin: Annotated[int, Form()]):
    data = (supabase.table("empleado")
            .select("*")
            .eq("nombre", nombre)
            .eq("pin_acceso", pin)
            .execute())

    if not data.data:
        raise HTTPException(
            status_code=401, 
            detail=f"Credenciales incorrectas!."
        )
    return data.data
