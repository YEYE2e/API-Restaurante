# API Restaurante - El Chato Ranch
**API en Producción (Swagger UI):** [https://api-restaurante.fastapicloud.dev/docs#/](https://api-restaurante.fastapicloud.dev/docs#/)

Este es el backend para la gestión del restaurante de la reserva ecológica El Chato Ranch. Está desarrollado con FastAPI y utiliza Supabase (PostgreSQL) como base de datos.

La API se encarga de controlar el acceso de empleados, gestionar los platos del menú y procesar los pedidos de forma transaccional, validando que haya stock disponible en la base de datos antes de confirmar cada comanda.

## Estructura del proyecto

* `main.py`: Punto de entrada de la aplicación.
* `database.py`: Configuración y conexión con Supabase.
* `routers/`: Endpoints de la API (`empleados.py`, `menu.py`, `pedidos.py`).
* `models/`: Esquemas de Pydantic para validación de datos.
* `tests/`: Pruebas de seguridad y funcionamiento del flujo de pedidos.

## Configuración y arranque

1. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

2. Configura las credenciales de Supabase en un archivo `.env` en la raíz del proyecto:
   ```env
   SUPABASE_URL="https://tu-proyecto.supabase.co"
   SUPABASE_PUBLISHABLE_KEY="tu-clave-publica-de-supabase"
   ```

3. Inicia el servidor de desarrollo:
   ```bash
   fastapi dev main.py
   ```
   Una vez corriendo, puedes ver y probar los endpoints en: `http://127.0.0.1:8000/docs`

## Endpoints principales

* **Empleados**: Registro de áreas, creación de usuarios, login con PIN y baja lógica de personal.
* **Menú**: Registro y búsqueda de platos por nombre (ej. `/menu/?q=plato`).
* **Pedidos**: Creación de comandas (utiliza una función RPC en PostgreSQL para descontar stock de forma segura), consulta de pedidos activos y actualización de estados en formato UTC.

## Pruebas

Para ejecutar la suite de pruebas unitarias y de integración:

```bash
PYTHONPATH=. pytest tests/
```