# test_ocr

## Objetivo
Este proyecto automatiza la extracción y análisis de información financiera desde documentos PDF utilizando modelos de lenguaje (LLM) y embeddings de Azure. Permite obtener datos estructurados como balances y datos de empresa a partir de archivos escaneados.

## Instalación
1. Clona el repositorio.
2. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```
3. Configura las variables de entorno necesarias en un archivo `.env`.

## Uso
Ejecuta el pipeline principal con:
```
python d_agents.py
```
Asegúrate de tener los archivos PDF en la ruta esperada.

## Estructura principal
- `config.py`: Centraliza la configuración y la inicialización de clientes Azure.
- `a_embeddings_ocr.py`, `c_tools.py`, `d_agents.py`: Módulos principales del pipeline.
- `b_prompts.py`: Prompts utilizados para la extracción de información.

## Cambios recientes
- Centralización de la inicialización de Azure LLM y embeddings en `config.py`.
- Limpieza de imports y variables no utilizados.
- Simplificación del código.

## Pendientes
- Probar estructura antigua con formato txt, json.
- Integrar mejoras de la versión-02.
