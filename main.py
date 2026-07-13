# pyrefly: ignore [missing-import]
from fastapi import FastAPI
from routers.empleados import router as empleados_router
from routers.menu import router as menu_router
from routers.pedidos import router as pedidos_router

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "¡Hola, Fast API!"}

app.include_router(empleados_router)
app.include_router(menu_router)
app.include_router(pedidos_router)
