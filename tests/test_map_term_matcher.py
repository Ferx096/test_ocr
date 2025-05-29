import pytest
from map.map_test import financial_terms

def test_financial_terms_structure():
    assert "Balance general" in financial_terms
    assert "Estado de resultados" in financial_terms
