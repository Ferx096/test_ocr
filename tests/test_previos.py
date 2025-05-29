import pytest
from previo.a_embeddings_ocr import embeddings_guia as previo_embeddings_guia
from previo.config import get_llm as previo_get_llm

def test_previo_embeddings_guia():
    assert isinstance(previo_embeddings_guia("guia de prueba"), str)

def test_previo_get_llm():
    llm = previo_get_llm()
    assert llm is not None
