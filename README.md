# test_ocr

![Estado del proyecto](https://img.shields.io/badge/estado-en%20desarrollo-yellow)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Licencia](https://img.shields.io/badge/licencia-MIT-green)

## Descripción

**test_ocr** es una solución automatizada para extraer y analizar información financiera de documentos PDF escaneados, como balances y estados financieros. Utiliza OCR de Azure, embeddings y matching semántico para transformar documentos no estructurados en datos estructurados y exportarlos a Excel.

---

## Tabla de Contenidos
- [¿Para qué sirve?](#para-qué-sirve)
- [Ejemplo de uso](#ejemplo-de-uso)
- [Instalación y requisitos](#instalación-y-requisitos)
- [Configuración](#configuración)
- [Funcionamiento](#funcionamiento)
- [Componentes principales](#componentes-principales)
- [Solución de problemas](#solución-de-problemas)
- [Contribución](#contribución)
- [Licencia](#licencia)
- [Contacto](#contacto)

---

## ¿Para qué sirve?

- Digitalizar y estructurar información financiera contenida en PDFs escaneados.
- Facilitar el análisis, reporte y reutilización de datos financieros.
- Automatizar procesos que normalmente requieren revisión manual de documentos.

---

## Ejemplo de uso

### Entrada (PDF escaneado)

    document/estados_financieros__pdf_93834000_202403.pdf

### Salida (Excel generado)

    resultado.xlsx

El archivo Excel contendrá los datos extraídos y estructurados del PDF procesado, según la guía definida en `map/map_test.md`.

---

## Instalación y requisitos

1. Python 3.8 o superior
2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. (Opcional) Instala Tesseract OCR si tu sistema lo requiere:
4. Instala dependencias de desarrollo (para testing):
   ```bash
   pip install -r requirements-dev.txt
   ```

   - Ubuntu: `sudo apt-get install tesseract-ocr`
   - Windows: [Descargar instalador](https://github.com/tesseract-ocr/tesseract)

---

## Configuración

Crea un archivo `.env` en la raíz del proyecto con tus credenciales de Azure:

```
AZURE_OPENAI_KEY=tu_clave
AZURE_OPENAI_ENDPOINT=tu_endpoint
```

Asegúrate de que el archivo `.env` NO se suba al repositorio.

---

## Funcionamiento

1. Coloca los archivos PDF a procesar en la carpeta `document/`.
2. Ejecuta el pipeline principal:
   ```bash
   python g_main.py
   ```
3. El resultado se genera en un archivo Excel (`resultado.xlsx`).
4. Para ejecutar todos los tests automatizados:
   ```bash
   pytest
   ```
   Esto buscará y ejecutará todos los tests en la carpeta `tests/`.

---

## Componentes principales

- `a_ocr_extractor.py`: Extrae texto de PDFs usando Azure Document Intelligence.
- `b_embeddings.py`: Procesa la guía y genera embeddings para matching.
- `d_tools.py`: Herramientas para matching, validación y exportación a Excel.
- `g_main.py`: Orquesta el pipeline de procesamiento.
- `f_config.py`: Configuración y credenciales de Azure.
- `map/`: Utilidades para pruebas y mapeo de términos (incluye la guía en markdown).
- `document/`: Carpeta de entrada para los PDFs.
- `requirements.txt`: Lista de dependencias necesarias.

---

## Solución de problemas

- **Error: 'No se encuentra la variable AZURE_OPENAI_KEY'**
  - Verifica que tu archivo `.env` esté correctamente configurado y en la raíz del proyecto.
- **OCR no reconoce bien los números**
  - Asegúrate de que el PDF tenga buena calidad. Considera preprocesar la imagen.
- **Problemas de dependencias**
  - Reinstala los paquetes con `pip install -r requirements.txt`.

---

## Contribución

¡Las contribuciones son bienvenidas!

1. Haz un fork del repositorio
2. Crea una rama para tu feature o fix
3. Haz tus cambios y commitea de forma descriptiva
4. Haz push a tu rama y abre un Pull Request

Por favor, sigue el estilo de código y documenta tus funciones.

---

## WORKFLOW

1. El usuario coloca el PDF a procesar en la carpeta `document/`.
2. El sistema extrae el texto usando Azure Document Intelligence.
3. Se utiliza la guía (`map/map_test.md`) para identificar y mapear los conceptos clave mediante embeddings y matching semántico.
4. Los datos estructurados se exportan a un archivo Excel (`resultado.xlsx`).
---

## Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo LICENSE para más detalles.

---

## Contacto

Para dudas o soporte, contacta a ferx096@gmail.com o abre un issue en GitHub.
