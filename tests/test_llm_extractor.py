import pytest
from llm_extractor import get_llm, extract_financial_info_from_pdf, classify_term_with_llm

def test_get_llm():
    llm = get_llm()
    assert llm is not None

def test_extract_financial_info_from_pdf():
    result = extract_financial_info_from_pdf("document/stados_financieros__pdf_93834000_202403.pdf")
    assert isinstance(result, dict)

def test_classify_term_with_llm():
    result = classify_term_with_llm("Activo", "1000", {"Activo": "Asset"})
    assert isinstance(result, str)
