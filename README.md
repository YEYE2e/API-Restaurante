# API Restaurante - El Chato Ranch

## Descripcion General
El Chato Ranch es una reserva ecologica que cuenta con una seccion de restaurante y venta de recuerdos para turistas. El giro del negocio es turistico, gastronomico y de comercio minorista mediante la venta de recuerdos.

Este proyecto se centra especificamente en la gestion del servicio del restaurante (sector gastronomico).

## Funcionalidades Principales
* Gestion de empleados y control de acceso.
* Administracion y busqueda de items del menu.
* Registro y actualizacion de pedidos de forma transaccional mediante funciones RPC (validando stock disponible).
* Control de marcas de tiempo en formato UTC para evitar problemas de desfase horario.

## Tecnologias
* FastAPI
* Supabase (PostgreSQL)
* Pydantic
* Pytest

## Pruebas
Para correr los tests automatizados de seguridad y funcionalidad:
```bash
PYTHONPATH=. .venv/bin/pytest tests/
```