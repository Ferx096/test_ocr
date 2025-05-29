import pytest
from b_embeddings import embeddings_guia, search_vectorestore

def test_embeddings_guia():
    assert isinstance(embeddings_guia("guia de prueba"), str)

def test_search_vectorestore():
    with open("document/stados_financieros__pdf_93834000_202403.pdf", "rb") as f:
        pdf_bytes = f.read()
    result = search_vectorestore(pdf_bytes, "guia de prueba")
    assert result is not None
