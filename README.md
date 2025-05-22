# test_ocr: Extracción Inteligente de Balances Financieros

## Instalación de dependencias

```bash
pip install -r requirements_final.txt
```

## Ejecución del pipeline principal

Para extraer los datos de empresa y balance general de un PDF financiero:

```bash
python3 rag_balance_pipeline.py --input_pdf document/estados_financieros__pdf_93834000_202403.pdf --output_csv extracted_terms.csv --output_xlsx balance_rag.xlsx --debug
```

- Cambia el valor de `--input_pdf` si deseas analizar otro archivo PDF.
- Los resultados estarán en `extracted_terms.csv` (términos y valores extraídos) y `balance_rag.xlsx` (balance estructurado por categoría).

## Archivos de salida
- `extracted_terms.csv`: Términos, valores, categorías y logs de matching.
- `balance_rag.xlsx`: Balance general estructurado (activos, pasivos, patrimonio, otros).
- Archivos de debug: `ocr_debug_*.txt` para trazabilidad y diagnóstico.

## Notas
- El pipeline utiliza OCR, matching flexible (fuzzy, embeddings, LLM) y un glosario inteligente basado en `map/map_test.json`.
- Si tienes problemas con dependencias, revisa y reinstala usando `requirements_final.txt`.
