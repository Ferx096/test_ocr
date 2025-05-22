import os
import json
from llm_extractor import extract_financial_info_from_pdf

def test_llm_extractor():
    # Cambia la ruta a un PDF de ejemplo real en tu carpeta 'document'
    pdf_path = os.path.join('document', 'ejemplo_balance.pdf')
    if not os.path.exists(pdf_path):
        print(f"No se encuentra el PDF de prueba: {pdf_path}")
        return
    result = extract_financial_info_from_pdf(pdf_path)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    assert result is not None
    assert 'company_name' in result
    assert 'activos' in result
    assert 'pasivos' in result
    assert 'patrimonio' in result

if __name__ == "__main__":
    test_llm_extractor()
