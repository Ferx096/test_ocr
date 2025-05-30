import pytest
import json

def test_map_test_md_exists():
    with open("map/map_test.md", "r", encoding="utf-8") as f:
        content = f.read()
    assert "Balance general" in content

def test_map_test_md_content():
    with open("map/map_test.md", "r", encoding="utf-8") as f:
        content = f.read()
    # Validar que contiene secciones clave
    assert "estructura_ejemplo" in content
    assert "activo corriente".lower() in content.lower()
    assert "pasivo corriente".lower() in content.lower()
    assert "patrimonio".lower() in content.lower()
    assert "sinonimos" in content
    # Validar que hay al menos una tabla o lista de cuentas
    assert "- Efectivo y equivalentes" in content
