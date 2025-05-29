import pytest
from a_embeddings_ocr import embeddings_guia, extract_text_from_pdf_azure, concat_text, search_vectorestore

def test_embeddings_guia():
    assert isinstance(embeddings_guia("guia de prueba"), str)

def test_extract_text_from_pdf_azure():
    with open("document/estados_financieros__pdf_93834000_202403.pdf", "rb") as f:
        pdf_bytes = f.read()
    result = extract_text_from_pdf_azure(pdf_bytes)
    assert isinstance(result, str)

def test_concat_text():
    with open("document/estados_financieros__pdf_93834000_202403.pdf", "rb") as f:
        pdf_bytes = f.read()
    result = concat_text(pdf_bytes)
    assert isinstance(result, str)

def test_search_vectorestore():
    with open("document/estados_financieros__pdf_93834000_202403.pdf"pyt, "rb") as f:
        pdf_bytes = f.read()
    result = search_vectorestore(pdf_bytes)
    assert result is not None
