import os
from a_embeddings_ocr import extract_text_from_pdf_azure
from langchain_openai import AzureChatOpenAI
import logging
import json

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def get_llm():
    return AzureChatOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_version=os.getenv("OPENAI_API_VERSION"),
        deployment_name=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
        model_name="gpt-4",
    )

# Prompt para extracción robusta de datos clave (nombre, RUT, fecha, activos, pasivos, patrimonio)
EXTRACTION_PROMPT = '''
Eres un agente experto en extraer información financiera clave de documentos. Dado el siguiente texto extraído por OCR (incluyendo tablas en markdown), extrae:
- Nombre de la empresa
- RUT
- Fecha del reporte
- Activos (total)
- Pasivos (total)
- Patrimonio (total)

Considera que los nombres pueden variar mucho (sinónimos, abreviaturas, etc). Devuelve un JSON con los siguientes campos:
{
  "company_name": ...,
  "company_rut": ...,
  "report_date": ...,
  "activos": ...,
  "pasivos": ...,
  "patrimonio": ...
}
Si algún campo no se encuentra, pon "No especificado". No expliques nada, solo el JSON.

Texto extraído:
"""
{document_text}
"""
'''

def extract_financial_info_from_pdf(pdf_path):
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    ocr_result = extract_text_from_pdf_azure(pdf_bytes)
    if not ocr_result or "full_text" not in ocr_result:
        logger.error("No se pudo extraer texto del PDF.")
        return None
    # Concatenar texto y tablas markdown
    full_text = ocr_result["full_text"]
    tables = ocr_result.get("tables_data", [])
    tables_md = ""
    import pandas as pd
    for table in tables:
        max_row = max(cell["row_index"] for cell in table) + 1
        max_col = max(cell["column_index"] for cell in table) + 1
        matrix = [["" for _ in range(max_col)] for _ in range(max_row)]
        for cell in table:
            row, col = cell["row_index"], cell["column_index"]
            matrix[row][col] = cell["content"]
        df = pd.DataFrame(matrix)
        tables_md += df.to_markdown(index=False) + "\n\n"
    document_text = full_text + "\n\n" + tables_md
    llm = get_llm()
    prompt = EXTRACTION_PROMPT.format(document_text=document_text)
    logger.info("Enviando prompt al LLM para extracción financiera clave...")
    response = llm.invoke(prompt)
    # Buscar JSON en la respuesta
    import re
    match = re.search(r'\{[\s\S]*\}', str(response))
    if match:
        try:
            return json.loads(match.group(0))
        except Exception as e:
            logger.error(f"Error al parsear JSON: {e}")
            return match.group(0)
    return response


def classify_term_with_llm(term, value, context_glossary):
    """
    Usa un LLM para clasificar un término y valor, usando el glosario como contexto.
    Devuelve: {'matched_term': ..., 'category': ..., 'score': ...}
    """
    llm = get_llm()
    # Construir prompt con contexto del glosario
    glossary_str = '\n'.join([f"- {k}" for k in context_glossary])
    prompt = f"""
Eres un experto en contabilidad. Clasifica el siguiente término y valor extraído de un balance financiero, usando el glosario proporcionado. Devuelve SOLO un JSON válido, con comillas dobles, sin texto extra, solo el objeto, con las claves: matched_term, category (como lista: [sección, bloque, subbloque]), y score (1.0 si estás seguro, 0.5 si es dudoso).

Ejemplo de respuesta válida:
{{"matched_term": "efectivo y equivalentes", "category": ["ACTIVOS", "CORRIENTES", "EFECTIVO"], "score": 1.0}}

Término: {term}
Valor: {value}

Glosario:
{glossary_str}
"""
    logger.info(f"Prompt LLM clasificación término: {term}")
    response = llm.invoke(prompt)
    logger.info(f"Respuesta cruda LLM: {response}")
    import re, json
    # Intentar extraer el primer objeto JSON válido de la respuesta
    import json
    import re
    json_candidates = re.findall(r'\{[\s\S]*?\}', str(response))
    for candidate in json_candidates:
        try:
            return json.loads(candidate)
        except Exception as e:
            try:
                cleaned = candidate.replace("'", '"')
                return json.loads(cleaned)
            except Exception:
                continue
    logger.error(f"No se pudo parsear ningún JSON válido en la respuesta LLM")
    return {'matched_term': None, 'category': None, 'score': 0.0}

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python llm_extractor.py <ruta_pdf>")
        exit(1)
    result = extract_financial_info_from_pdf(sys.argv[1])
    print(json.dumps(result, ensure_ascii=False, indent=2))
