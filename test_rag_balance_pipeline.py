import os
import pandas as pd
from rag_balance_pipeline import balance

def test_balance_not_empty():
    assert any(balance[k] for k in ['activos', 'pasivos', 'patrimonio']), "El balance está vacío. Revisa el OCR o el matcher."

def test_balance_keys():
    for k in ['activos', 'pasivos', 'patrimonio', 'otros']:
        assert k in balance, f"Falta la clave {k} en el balance."

def test_balance_values_are_str():
    for k in ['activos', 'pasivos', 'patrimonio']:
        for v in balance[k].values():
            assert isinstance(v, str), f"El valor {v} no es string."

def test_exported_files():
    assert os.path.exists("extracted_terms.csv"), "No se generó extracted_terms.csv"
    assert os.path.exists("balance_rag.xlsx"), "No se generó balance_rag.xlsx"
