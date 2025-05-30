import pytest
from previo.a_embeddings_ocr import embeddings_guia as previo_embeddings_guia
from previo.config import get_llm as previo_get_llm

def test_previo_embeddings_guia():
    result = previo_embeddings_guia("guia de prueba")
    from langchain.schema import Document
    assert isinstance(result, list)
    assert all(isinstance(doc, Document) for doc in result)

def test_previo_get_llm():
    llm = previo_get_llm()
    assert llm is not None
