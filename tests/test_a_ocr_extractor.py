import pytest
from a_ocr_extractor import extract_text_from_pdf_azure, concat_text

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
