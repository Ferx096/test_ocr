import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from b_embeddings import embeddings_guia
from d_tools import find_matches_in_ocr
from f_config import get_embedding

# Ejemplo mínimo de guía y OCR para test unitario
GUIDE_MD = """
# Activos
- Caja y Bancos
- Cuentas por Cobrar
# Pasivos
- Proveedores
- Deudas Bancarias
"""

OCR_TEXT = """
Caja y Bancos 1.234.567\nCuentas por Cobrar 890.123\nProveedores 456.789\nDeudas Bancarias 123.456\nOtros 999\n"""

def test_find_matches_in_ocr_basic():
    embedding = get_embedding()
    guide_docs = embeddings_guia(GUIDE_MD)
    matches = find_matches_in_ocr(OCR_TEXT, guide_docs, embedding=embedding, threshold_fuzzy=70, threshold_semantic=0.5, top_k=1)
    # Debe encontrar 4 matches válidos (sin "Otros")
    assert len(matches) == 4
    nombres = [m['guia_chunk'].lower() for m in matches]
    assert any('caja' in n for n in nombres)
    assert any('cuentas' in n for n in nombres)
    assert any('proveedores' in n for n in nombres)
    assert any('deudas' in n for n in nombres)
    # Los valores deben ser numéricos y positivos
    for m in matches:
        assert isinstance(m['value'], float)
        assert m['value'] > 0

