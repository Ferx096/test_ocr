import os
import logging
from a_embeddings_ocr import extract_text_from_pdf_azure
from ocr_preprocess import preprocess_ocr_result
from map.term_matcher import TermMatcher
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Configuración de paths y modelos
PDF_PATH = os.getenv("PDF_PATH", "document/estados_financieros__pdf_93834000_202403.pdf")
MAP_JSON_PATH = os.getenv("MAP_JSON_PATH", "map/map_test.json")

# 1. Extraer texto y tablas del PDF
with open(PDF_PATH, "rb") as f:
    pdf_bytes = f.read()
ocr_result = extract_text_from_pdf_azure(pdf_bytes)
if not ocr_result or "full_text" not in ocr_result:
    # DEBUG: Guardar texto OCR crudo para inspección
    with open("ocr_debug_full_text.txt", "w", encoding="utf-8") as dbg:
        dbg.write(str(ocr_result))
    logger.error("No se pudo extraer texto del PDF.")
    exit(1)
# DEBUG: Guardar texto OCR crudo para inspección
with open("ocr_debug_full_text.txt", "w", encoding="utf-8") as dbg:
    dbg.write(ocr_result.get("full_text", ""))

# 2. Preprocesar texto OCR
preproc = preprocess_ocr_result(ocr_result)
lines = preproc['lines']
tables = preproc['tables']
raw_text = preproc['raw']
from ocr_preprocess import extract_term_value_candidates, extract_term_value_pairs, extract_table_rows

# Extraer candidatos a pares término-valor de todo el texto crudo
candidates = extract_term_value_candidates(raw_text)
# Extraer pares término-valor
term_value_pairs = extract_term_value_pairs(raw_text)
# Extraer filas de tabla
rows = extract_table_rows(raw_text)

# DEBUG: Guardar candidatos extraídos antes del matching
with open("ocr_debug_candidates.txt", "w", encoding="utf-8") as dbg:
    for c in candidates:
        dbg.write(str(c) + "\n")
# DEBUG: Guardar pares término-valor extraídos
with open("ocr_debug_term_value_pairs.txt", "w", encoding="utf-8") as dbg:
    for pair in term_value_pairs:
        dbg.write(str(pair) + "\n")
# DEBUG: Guardar filas de tabla extraídas
with open("ocr_debug_table_rows.txt", "w", encoding="utf-8") as dbg:
    for row in rows:
        dbg.write(str(row) + "\n")

# DEBUG: Guardar pares extraídos por heurística flexible
from ocr_preprocess import extract_flexible_term_value_pairs
flex_pairs = extract_flexible_term_value_pairs(raw_text)
with open("ocr_debug_flexible_pairs.txt", "w", encoding="utf-8") as dbg:
    for pair in flex_pairs:
        dbg.write(str(pair) + "\n")

# DEBUG: Guardar pares extraídos por agrupación multilineal
from ocr_preprocess import extract_multiline_term_value_pairs
multi_pairs = extract_multiline_term_value_pairs(raw_text)
with open("ocr_debug_multiline_pairs.txt", "w", encoding="utf-8") as dbg:
    for pair in multi_pairs:
        dbg.write(str(pair) + "\n")

from ocr_preprocess import debug_multiline_candidates
debug_multiline_candidates(raw_text)

from ocr_preprocess import extract_flatline_term_value_groups
flatline_groups = extract_flatline_term_value_groups(raw_text)
with open("ocr_debug_flatline_groups.txt", "w", encoding="utf-8") as dbg:
    for group in flatline_groups:
        dbg.write(str(group) + "\n")

# Extraer candidatos a pares término-valor de todo el texto crudo
candidates = extract_term_value_candidates(raw_text)

from ocr_preprocess import extract_term_value_pairs
# Extraer pares término-valor
term_value_pairs = extract_term_value_pairs(raw_text)

from ocr_preprocess import extract_table_rows
# Extraer filas de tabla
rows = extract_table_rows(raw_text)


# 3. Inicializar el matcher inteligente
matcher = TermMatcher(map_json_path=MAP_JSON_PATH)

# 4. Buscar términos y valores en líneas/tablas
extracted = []
import re
import re
import logging
logging.basicConfig(filename='rag_balance_debug.log', level=logging.INFO, format='%(asctime)s %(message)s')

regexes = [
    r"(.+?)[\s:]+([\(\-]?[\d\.,]+[\)]?)$",  # original
    r"(.+?)\s+([\d\.,]+)$",                  # término seguido de número
    r"(.+?):\s*([\d\.,]+)$",                 # término: valor
    r"(.+?)\s*\t\s*([\d\.,]+)$",           # término\tvalor
]

# Usar filas de tabla si existen, si no, usar pares término-valor
if rows:
    for cols in rows:
        term = cols[0]
        value = cols[-1]
        line = f"{term} {value}"
        logging.info(f"LINE: {line}")
        m = None
        for rx in regexes:
            m = re.match(rx, line)
            if m:
                break
        if not m:
            continue
        original, value = m.group(1).strip(), m.group(2).replace('.', '').replace(',', '.')
        match_result = matcher.match(original, return_log=True)
        matched_term = match_result['term'] if match_result['score'] > 0.3 else None
        category = match_result.get('category')
        score = match_result['score']
        log = match_result.get('log')
        extracted.append({
            'original': original,
            'value': value,
            'matched_term': matched_term,
            'category': category,
            'score': score,
            'log': log
        })
else:
    for term, nums in term_value_pairs:
        value = nums[-1]
        line = f"{term} {value}"
        logging.info(f"LINE: {line}")
        m = None
        for rx in regexes:
            m = re.match(rx, line)
            if m:
                break
        if not m:
            continue
        original, value = m.group(1).strip(), m.group(2).replace('.', '').replace(',', '.')
        match_result = matcher.match(original, return_log=True)
        matched_term = match_result['term'] if match_result['score'] > 0.3 else None
        category = match_result.get('category')
        score = match_result['score']
        log = match_result.get('log')
        extracted.append({
            'original': original,
            'value': value,
            'matched_term': matched_term,
            'category': category,
            'score': score,
            'log': log
        })


logging.info(f"MATCHER TERMS: {matcher.terms[:10]} ... total: {len(matcher.terms)}")

# 5. Agrupar por categoría estándar
balance = {'activos': {}, 'pasivos': {}, 'patrimonio': {}, 'otros': {}}
for item in extracted:
    if not item['matched_term'] or not item['category']:
        balance['otros'][item['original']] = item['value']
        continue
    section, block, subblock = item['category']
    cat = f"{section} {block} {subblock}".lower() if subblock else f"{section} {block}".lower()
    # Clasificación inteligente usando RAG+LLM: si la categoría contiene palabras clave
    if any(x in cat for x in ['activo', 'asset']):
        balance['activos'][item['matched_term']] = item['value']
    elif any(x in cat for x in ['pasivo', 'liabil']):
        balance['pasivos'][item['matched_term']] = item['value']
    elif any(x in cat for x in ['patrimonio', 'equity', 'capital']):
        balance['patrimonio'][item['matched_term']] = item['value']
    else:
        balance['otros'][item['original']] = item['value']

# 6. Guardar resultados y logging
logger.info(f"Balance estructurado: {balance}")
pd.DataFrame(extracted).to_csv("extracted_terms.csv", index=False)

# 7. (Opcional) Guardar balance en Excel
with pd.ExcelWriter("balance_rag.xlsx") as writer:
    for k in ['activos', 'pasivos', 'patrimonio', 'otros']:
        pd.DataFrame(list(balance[k].items()), columns=["Cuenta", "Valor"]).to_excel(writer, sheet_name=k, index=False)

print("Pipeline RAG+OCR+map_test.json ejecutado. Resultados en extracted_terms.csv y balance_rag.xlsx")
