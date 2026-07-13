from fastapi import FastAPI, Form, Response, HTTPException, status
from typing import Annotated
from models.area import Area
from models.empleado import Empleado
from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()
supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_PUBLISHABLE_KEY"))
app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "¡Hola, Fast API!"}


@app.post("/area/")
def create_area(area: Area):
    data = supabase.table("area").insert({
        "nombre": area.nombre
    }).execute()
    return data.data


@app.post("/empleado/")
def create_user(area_busqueda:str, empleado: Empleado):
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
    

@app.post("/empleado/login")
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


    
