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


# Casos borde y robustez
GUIDE_EDGE = """
- Caja
- Bancos
- Cuentas por Cobrar
- Inventario
- Proveedores
- Deudas Bancarias
- Otros Pasivos
"""

OCR_EDGE = """
CAJA 0
BANCOS 1.000,50
Cuentas por cobrar 0.00
Inventario -123
Proveedores 999.999,99
Deudas Bancarias 0
Otros Pasivos 123,45
No relacionado 555
"""

def test_find_matches_in_ocr_edge_cases():
    embedding = get_embedding()
    guide_docs = embeddings_guia(GUIDE_EDGE)
    matches = find_matches_in_ocr(OCR_EDGE, guide_docs, embedding=embedding, threshold_fuzzy=60, threshold_semantic=0.5, top_k=1)
    # Debug: print all matches for inspection
    print('MATCHES:', matches)
    # Debe encontrar 7 matches válidos (sin "No relacionado")
    assert len(matches) == 7
    # Valores negativos y ceros deben ser float
    for m in matches:
        assert isinstance(m['value'], float)
    # Inventario debe ser negativo
    inv = [m for m in matches if 'inventario' in m['guia_chunk'].lower()][0]
    assert inv['value'] < 0
    # Bancos debe ser decimal
    bancos = [m for m in matches if 'bancos' in m['guia_chunk'].lower()][0]
    assert abs(bancos['value'] - 1000.50) < 0.01
    # Proveedores debe ser float grande
    prov = [m for m in matches if 'proveedores' in m['guia_chunk'].lower()][0]
    assert prov['value'] > 900000

# Exportación: simulación de estructura exportable
import pandas as pd

def test_export_matches_to_dataframe():
    embedding = get_embedding()
    guide_docs = embeddings_guia(GUIDE_MD)
    matches = find_matches_in_ocr(OCR_TEXT, guide_docs, embedding=embedding, threshold_fuzzy=70, threshold_semantic=0.5, top_k=1)
    df = pd.DataFrame(matches)
    assert not df.empty
    assert set(['guia_chunk', 'ocr_line', 'value']).issubset(df.columns)
    # Los valores exportados deben ser numéricos
    assert df['value'].apply(lambda x: isinstance(x, float)).all()

