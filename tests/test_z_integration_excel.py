import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/../'))
import pandas as pd
from e_agents import node_final

def test_trivial():
    assert 1 == 1

def test_excel_generation_and_content(tmp_path):
    # Estado simulado con datos reales
    state = {
        "nombre_compañia": "TestCo",
        "rut_compañia": "12345678-9",
        "fecha_reporte": "2024-01-01",
        "creacion_report": "2024-01-02 12:00:00",
        "balance_general": [
            {"caja": 1000, "bancos": 2000, "total_activos": 3000},
            {"deuda": 500, "total_pasivos": 500},
            {"capital": 2500, "total_patrimonio": 2500}
        ]
    }
    # Ejecutar el nodo final para generar el Excel
    result = node_final(state)
    # Guardar el archivo temporalmente
    excel_path = tmp_path / "Balance_empresa_TestCo.xlsx"
    with open(excel_path, "wb") as f:
        f.write(result.update["excel_bytes"])
    # Leer el archivo y verificar contenido
    df = pd.read_excel(excel_path, sheet_name="Balance", header=None, keep_default_na=False)
    # Verifica que los valores no sean 0 o None en las filas de balance
    assert (df.iloc[8:11, 1:4] != 0).all().all(), "Hay valores 0 en el balance"
    assert (df.iloc[8:11, 1:4].notnull()).all().all(), "Hay valores None en el balance"
    # Limpieza
    os.remove(excel_path)
