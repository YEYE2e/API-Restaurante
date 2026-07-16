import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app

client = TestClient(app)

@patch('routers.pedidos.supabase')
def test_get_pedidos_activos(mock_supabase):
    # Simula el retorno de supabase.table().select().neq().execute()
    mock_response = MagicMock()
    mock_response.data = [
        {
            "id": 1,
            "estado_comanda": "En Preparación",
            "prioridad": "Alta",
            "empleado": {"nombre": "Juan Pérez"},
            "detalle_pedido": [
                {
                    "id": 10,
                    "pedido_id": 1,
                    "cantidad": 2,
                    "notas_especificas": "Sin cebolla",
                    "item_menu": {"nombre": "Hamburguesa Especial"}
                }
            ]
        }
    ]
    
    # Encadena los retornos para simular la API fluida de Supabase
    mock_supabase.table.return_value.select.return_value.neq.return_value.execute.return_value = mock_response

    response = client.get("/pedidos/activos")
    
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["estado_comanda"] == "En Preparación"
    assert response.json()[0]["empleado"]["nombre"] == "Juan Pérez"
    assert response.json()[0]["detalle_pedido"][0]["item_menu"]["nombre"] == "Hamburguesa Especial"
    
    mock_supabase.table.assert_called_with("pedido")
    mock_supabase.table.return_value.select.assert_called_with("*, empleado:emisor_id(nombre), detalle_pedido(*, item_menu:item_menu_id(nombre))")
    mock_supabase.table.return_value.select.return_value.neq.assert_called_with("estado_comanda", "Despachado")


@patch('routers.pedidos.supabase')
def test_update_pedido_estado(mock_supabase):
    # Simula el retorno de la actualización
    mock_response = MagicMock()
    mock_response.data = [
        {
            "id": 1,
            "estado_comanda": "Listo",
            "fecha_actualizacion": "2026-07-13T16:27:03"
        }
    ]
    
    # Encadena los retornos para simular la API fluida de Supabase
    mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_response

    payload = {
        "estado_comanda": "Listo"
    }
    
    response = client.patch("/pedidos/1/estado", json=payload)
    
    assert response.status_code == 200
    assert response.json()["estado_comanda"] == "Listo"
    
    mock_supabase.table.assert_called_with("pedido")
    mock_supabase.table.return_value.update.return_value.eq.assert_called_with("id", 1)
