# test_ocr

## Descripción

**test_ocr** es una herramienta para la extracción automatizada y análisis de información financiera desde documentos PDF escaneados, utilizando modelos de lenguaje (LLM) y embeddings de Azure. El objetivo es transformar documentos no estructurados (como balances y estados financieros) en datos estructurados y útiles para análisis o integración en otros sistemas.

## Características principales

- Extracción OCR avanzada desde PDFs escaneados.
- Uso de modelos de lenguaje y embeddings de Azure para mejorar la precisión.
- Pipeline modular y fácil de adaptar a otros tipos de documentos.
- Soporte para múltiples formatos de salida (JSON, TXT, etc.).

## Diagrama de flujo

```
PDF -> OCR -> Embeddings -> LLM Extraction -> Datos estructurados (JSON/TXT)
```

## Ejemplo de uso

Supón que tienes un PDF de un balance financiero. El sistema extraerá los datos clave y los convertirá en un archivo JSON estructurado, listo para análisis.

## Instalación

1. Clona el repositorio:
   ```bash
   git clone https://github.com/Ferx096/test_ocr.git
   cd test_ocr
   ```
2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Configura las variables de entorno necesarias en un archivo `.env` (ver sección de configuración).

## Configuración

Debes crear un archivo `.env` con tus credenciales de Azure y otros parámetros necesarios. Ejemplo:

```
AZURE_OPENAI_KEY=tu_clave
AZURE_OPENAI_ENDPOINT=tu_endpoint
...
```

Asegúrate de tener los archivos PDF en la carpeta `document/`.

## Uso

Ejecuta el pipeline principal con:
```bash
python d_agents.py
```
Los resultados se guardarán en archivos de salida en el formato especificado.

## Estructura del repositorio

- `a_embeddings_ocr.py`: Generación de embeddings y procesamiento OCR.
- `d_agents.py`: Orquestador principal del pipeline.
- `f_config.py`: Configuración y credenciales de Azure.
- `map/`: Utilidades para mapeo y pruebas.
- `document/`: Carpeta donde colocar los PDFs a procesar.
- `requirements.txt`: Dependencias del proyecto.

## Contribución

¡Las contribuciones son bienvenidas! Por favor, abre un issue o un pull request para sugerencias o mejoras.

## Licencia

[MIT](LICENSE) (o la que corresponda)

## Contacto

Para soporte o preguntas, contacta a ferx096@gmail.com o abre un issue en GitHub.
