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
## Documentación de módulos principales

- El flujo principal está en `rag_balance_pipeline.py`, que orquesta la extracción, preprocesamiento, matching y exportación de resultados.
- Las funciones de parsing están en `parsing_tools.py`, los agentes en `agent_tools.py` y las utilidades en `utils_tools.py`. El archivo `c_tools.py` se mantiene solo para compatibilidad temporal.
- El matching semántico de términos está en `map/term_matcher.py` y el glosario inteligente en `rag_glossary.py`.
- Los prompts y plantillas de extracción están en `b_prompts.py`.
- El módulo `llm_extractor.py` contiene utilidades para extracción robusta usando LLMs.
- Los logs estructurados se generan con `utils_logging.py`.

## Mejora de modularidad y documentación

- Se refactorizó `c_tools.py` en submódulos: `parsing_tools.py`, `agent_tools.py` y `utils_tools.py`.
- Se mejorará el manejo de errores y el logging en los módulos principales.
- Se unificará el idioma a español en variables, funciones y prompts.
- Se ampliarán los tests para cubrir los módulos principales.

## Diagrama de flujo de búsqueda semántica

Este diagrama describe el flujo de trabajo para categorizar términos financieros utilizando técnicas de búsqueda semántica, incluyendo coincidencias difusas, embeddings y modelos de lenguaje.


```mermaid
flowchart TD
    A["Término de entrada\n(\"caja bancaria\")"]
    A --> B["TermMatcher\nFuzzy + Embedding Matching\n(OpenAI)"]
    B --> C{"¿Coincidencia encontrada?"}
    C -- Sí --> D["Categoría asignada\nEj.: Activo Corriente"]
    C -- No --> E["GlossaryRAG\nSemantic Search\n(MiniLM)"]
    E --> F["Términos similares sugeridos\nEj.: \"efectivo y equivalentes\""]
