import json
from a_ocr_extractor import extract_text_from_pdf_azure
from b_embeddings import embeddings_guia
from d_tools import find_matches_in_ocr, ensure_totals, exportar_a_excel
from f_config import get_embedding

# 1. Carga la guía (markdown)
with open("map/map_test.md", encoding="utf-8") as f:
    guia_data = f.read()

# 2. Carga el PDF
with open("document/estados_financieros__pdf_93834000_202403.pdf", "rb") as f:
    pdf_bytes = f.read()

# 3. Extrae el texto OCR
oct_result = extract_text_from_pdf_azure(pdf_bytes)
ocr_text = oct_result["full_text"]

# 4. Construye los documentos de la guía (desde markdown)
guide_docs = embeddings_guia(guia_data)

# 5. Matching y extracción
embedding_model = get_embedding()
resultados = find_matches_in_ocr(ocr_text, guide_docs, embedding=embedding_model)
resultados = ensure_totals(resultados)

# 6. Exporta a Excel
nombre_archivo = exportar_a_excel(resultados)
print(f"Balance exportado a {nombre_archivo}")

