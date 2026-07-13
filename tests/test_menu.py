import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Import app inside the test file or dynamically to ensure the patches apply correctly
with patch('database.supabase') as mock_db_supabase:
    # We patch before importing app to avoid import-time side-effects of real supabase init if needed,
    # but since main imports routers, patching the router's imported name directly is cleanest.
    pass

from main import app

client = TestClient(app)

@patch('routers.menu.supabase')
def test_get_menu_items(mock_supabase):
    # Simula el retorno de supabase.table().select().execute()
    mock_response = MagicMock()
    mock_response.data = [
        {"id": 1, "nombre": "Pizza Margherita", "descripcion": "Salsa de tomate y queso", "precio": 12.50, "stock_disponible": 15, "categoria": "Pizzas"}
    ]
    mock_supabase.table.return_value.select.return_value.execute.return_value = mock_response

    response = client.get("/menu/")
    
    assert response.status_code == 200
    assert response.json() == [
        {"id": 1, "nombre": "Pizza Margherita", "descripcion": "Salsa de tomate y queso", "precio": 12.50, "stock_disponible": 15, "categoria": "Pizzas"}
    ]
    mock_supabase.table.assert_called_once_with("item_menu")
    mock_supabase.table.return_value.select.assert_called_once_with("*")


@patch('routers.menu.supabase')
def test_create_menu_item(mock_supabase):
    # Simula el retorno de supabase.table().insert().execute()
    mock_response = MagicMock()
    mock_response.data = [
        {"id": 2, "nombre": "Hamburguesa Especial", "descripcion": "Con papas fritas", "precio": 10.00, "stock_disponible": 20, "categoria": "Burgers"}
    ]
    mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_response

    payload = {
        "id": 2,
        "nombre": "Hamburguesa Especial",
        "descripcion": "Con papas fritas",
        "precio": 10.00,
        "stock_disponible": 20,
        "categoria": "Burgers"
    }
    
    response = client.post("/menu/", json=payload)
    
    assert response.status_code == 201
    assert response.json() == [
        {"id": 2, "nombre": "Hamburguesa Especial", "descripcion": "Con papas fritas", "precio": 10.00, "stock_disponible": 20, "categoria": "Burgers"}
    ]
    mock_supabase.table.assert_called_once_with("item_menu")
    mock_supabase.table.return_value.insert.assert_called_once_with(payload)
