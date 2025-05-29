# Explicación del Proyecto: test_ocr

## ¿Qué es test_ocr?

**test_ocr** es una solución automatizada para extraer y analizar información financiera de documentos PDF escaneados, como balances y estados financieros. Utiliza tecnologías de OCR (Reconocimiento Óptico de Caracteres), modelos de lenguaje (LLM) y embeddings de Azure para transformar documentos no estructurados en datos estructurados y útiles.

## ¿Para qué sirve?

- Digitalizar y estructurar información financiera contenida en PDFs escaneados.
- Facilitar el análisis, reporte y reutilización de datos financieros.
- Automatizar procesos que normalmente requieren revisión manual de documentos.

## ¿Cómo funciona?

1. **Carga de documentos**: El usuario coloca los archivos PDF en la carpeta `document/`.
2. **Procesamiento OCR**: El sistema convierte las imágenes de texto en texto digital.
3. **Embeddings y LLM**: Se utilizan modelos de Azure para comprender el contexto y extraer información relevante.
4. **Estructuración**: Los datos extraídos se organizan en formatos como JSON o TXT para su análisis posterior.

## Componentes principales

- `a_embeddings_ocr.py`: Procesa los PDFs y genera embeddings para mejorar la extracción.
- `d_agents.py`: Orquesta el pipeline de procesamiento.
- `f_config.py`: Configuración y credenciales de Azure.
- `map/`: Utilidades para pruebas y mapeo de términos.
- `document/`: Carpeta de entrada para los PDFs.
- `requirements.txt`: Lista de dependencias necesarias.

## ¿Qué tecnologías utiliza?

- Python 3
- Azure OpenAI (LLM y embeddings)
- OCR (Reconocimiento Óptico de Caracteres)
- Pandas para manipulación de datos

## ¿Cómo se usa?

1. Instala las dependencias con `pip install -r requirements.txt`.
2. Configura tus credenciales de Azure en un archivo `.env`.
3. Coloca los PDFs a procesar en la carpeta `document/`.
4. Ejecuta el pipeline con `python d_agents.py`.
5. Revisa los resultados generados en los archivos de salida.

## Ventajas

- Ahorra tiempo y reduce errores humanos en la digitalización de datos financieros.
- Modular y fácil de adaptar a otros tipos de documentos.
- Escalable para grandes volúmenes de archivos.

## Contacto

Para dudas o soporte, contacta a ferx096@gmail.com o abre un issue en GitHub.
