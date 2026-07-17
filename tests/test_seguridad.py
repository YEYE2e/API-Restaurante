from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app

client = TestClient(app)

@patch("routers.empleados.supabase")
def test_login_seguro_oculta_pin(mock_supabase):
    # Simula que la consulta a supabase retorna el usuario sin exponer el pin
    mock_response = MagicMock()
    mock_response.data = [{
        "id": 1,
        "nombre": "Juan",
        "cargo": "Mesero",
        "estado": True,
        "area_id": 2
    }]
    mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_response

    response = client.post("/empleado/login", data={"nombre": "Juan", "pin": 1234})
    assert response.status_code == 200
    assert "pin_acceso" not in response.json()

@patch("routers.empleados.supabase")
def test_login_credenciales_invalidas(mock_supabase):
    # Simula que la consulta a supabase retorna una lista vacía indicando credenciales inválidas
    mock_response = MagicMock()
    mock_response.data = []
    mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_response

    response = client.post("/empleado/login", data={"nombre": "Juan", "pin": 9999})
    assert response.status_code == 401

def test_crear_pedido_cantidad_negativa():
    # Envía cantidad negativa (-2) para provocar un fallo en la validación de Pydantic
    payload = {
        "detalles": [
            {"item_menu_id": 1, "cantidad": -2}
        ]
    }
    response = client.post("/pedidos/", json=payload)
    assert response.status_code == 422

@patch("routers.menu.supabase")
def test_busqueda_menu(mock_supabase):
    # Simula que Supabase realiza la búsqueda con select().ilike().execute()
    mock_response = MagicMock()
    mock_response.data = [
        {"id": 1, "nombre": "Plato de prueba", "precio": 12.5}
    ]
    mock_supabase.table.return_value.select.return_value.ilike.return_value.execute.return_value = mock_response

    response = client.get("/menu/", params={"q": "test"})
    assert response.status_code == 200
    assert response.json() == [{"id": 1, "nombre": "Plato de prueba", "precio": 12.5}]

@patch("routers.pedidos.supabase")
def test_crear_pedido_exitoso(mock_supabase):
    # Simula una llamada exitosa al rpc "crear_pedido_con_stock"
    mock_response = MagicMock()
    mock_response.data = {"mensaje": "Comanda creada exitosamente", "pedido_id": 4}
    mock_supabase.rpc.return_value.execute.return_value = mock_response

    payload = {
        "emisor_id": 1,
        "prioridad": "Alta",
        "origen_pedido": "Mesa",
        "numero_mesa": "5",
        "detalles": [
            {"item_menu_id": 1, "cantidad": 2, "notas": "Sin sal"}
        ]
    }
    response = client.post("/pedidos/", json=payload)
    assert response.status_code == 201
    assert response.json() == {"mensaje": "Comanda creada exitosamente", "pedido_id": 4}

@patch("routers.pedidos.supabase")
def test_crear_pedido_sin_stock(mock_supabase):
    # Simula un error por falta de stock
    mock_exception = Exception("El plato Pasta no tiene stock suficiente.")
    mock_supabase.rpc.return_value.execute.side_effect = mock_exception

    payload = {
        "emisor_id": 1,
        "detalles": [
            {"item_menu_id": 1, "cantidad": 9999}
        ]
    }
    response = client.post("/pedidos/", json=payload)
    assert response.status_code == 400
    assert "stock suficiente" in response.json()["detail"]

@patch("routers.pedidos.supabase")
def test_crear_pedido_no_existe(mock_supabase):
    # Simula un error porque el plato no existe
    mock_exception = Exception("El plato con ID 99999 no existe.")
    mock_supabase.rpc.return_value.execute.side_effect = mock_exception

    payload = {
        "emisor_id": 1,
        "detalles": [
            {"item_menu_id": 99999, "cantidad": 1}
        ]
    }
    response = client.post("/pedidos/", json=payload)
    assert response.status_code == 400
    assert "no existe" in response.json()["detail"]

@patch("routers.pedidos.supabase")
def test_crear_pedido_error_interno(mock_supabase):
    # Simula un error interno de base de datos no relacionado con stock o existencia
    mock_exception = Exception("Conexión perdida con la base de datos.")
    mock_supabase.rpc.return_value.execute.side_effect = mock_exception

    payload = {
        "emisor_id": 1,
        "detalles": [
            {"item_menu_id": 1, "cantidad": 1}
        ]
    }
    response = client.post("/pedidos/", json=payload)
    assert response.status_code == 500
    assert "Error interno del servidor." in response.json()["detail"]

@patch("routers.pedidos.supabase")
def test_update_pedido_estado_utc(mock_supabase):
    # Simula una actualización exitosa del estado del pedido
    mock_response = MagicMock()
    mock_response.data = [{"id": 1, "estado_comanda": "Preparado", "fecha_actualizacion": "2026-07-17T20:30:00+00:00"}]
    mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_response

    response = client.patch("/pedidos/1/estado", json={"estado": "Preparado"})
    assert response.status_code == 200
    
    # Verifica que la actualización de Supabase haya sido llamada con fecha_actualizacion en formato UTC
    mock_supabase.table.assert_called_with("pedido")
    update_call = mock_supabase.table.return_value.update.call_args
    assert update_call is not None
    update_payload = update_call[0][0]
    assert "fecha_actualizacion" in update_payload
    # Comprueba que el timestamp incluya el offset de UTC (+00:00)
    assert "+00:00" in update_payload["fecha_actualizacion"]

