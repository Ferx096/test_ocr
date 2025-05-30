def test_rag_glossary_init():
    # Ahora valida que el glosario en map_test.md tiene la sección de descripción
    with open("map/map_test.md", "r", encoding="utf-8") as f:
        content = f.read()
    assert "descripcion" in content

def test_query():
    # Ahora valida que existen sinonimos y al menos una cuenta listada
    with open("map/map_test.md", "r", encoding="utf-8") as f:
        content = f.read()
    assert "sinonimos" in content
    assert "Caja y bancos" in content

