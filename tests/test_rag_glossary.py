import pytest
from rag_glossary import rag_glossary

def test_rag_glossary_init():
    glossary = rag_glossary("map/map_test.json")
    assert glossary is not None

def test_query():
    glossary = rag_glossary("map/map_test.json")
    result = glossary.query("Activo")
    assert isinstance(result, list)
