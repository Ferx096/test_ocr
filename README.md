# test_ocr

## Cambios recientes
- Centralización de la inicialización de Azure LLM y embeddings en `config.py` mediante las funciones `get_llm()` y `get_embedding()`.
- Eliminación de imports y variables no utilizados en los archivos principales (`a_embeddings_ocr.py`, `c_tools.py`, `d_agents.py`).
- Limpieza y simplificación del código para mayor mantenibilidad.

## Estructura principal
- Toda la configuración y la inicialización de clientes Azure se realiza desde `config.py`.
- Los módulos principales importan directamente `get_llm` y `get_embedding` desde `config.py`.

## Pendientes
1. Probar estructura antigua con formato txt, json junto para ver qué tal los resultados.
2. Probar combinar estructura de la version-02 en este formato y ver cómo se comporta.
3. Probar la versión-02 con el formato txt y observar resultados.
