# test_ocr

![Estado del proyecto](https://img.shields.io/badge/estado-en%20desarrollo-yellow)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Licencia](https://img.shields.io/badge/licencia-MIT-green)

## Descripción

**test_ocr** es una solución automatizada para extraer y analizar información financiera de documentos PDF escaneados, como balances y estados financieros. Utiliza tecnologías de OCR (Reconocimiento Óptico de Caracteres), modelos de lenguaje (LLM) y embeddings de Azure para transformar documentos no estructurados en datos estructurados y útiles.

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

    document/Yamas 2023 Balance Sheet.pdf

### Salida (JSON generado)

```json
{
  "empresa": "Ejemplo S.A.",
  "anio": 2024,
  "activo_total": 100000,
  "pasivo_total": 50000,
  "patrimonio": 50000
}
```

---

## Instalación y requisitos

1. Python 3.8 o superior
2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. (Opcional) Instala Tesseract OCR si tu sistema lo requiere:
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
   python d_agents.py
   ```
3. Los resultados se generan en archivos de salida (JSON/TXT) según la configuración.

---

## Componentes principales

- `a_embeddings_ocr.py`: Procesa los PDFs y genera embeddings para mejorar la extracción.
- `d_agents.py`: Orquesta el pipeline de procesamiento.
- `f_config.py`: Configuración y credenciales de Azure.
- `map/`: Utilidades para pruebas y mapeo de términos.
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

## Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo LICENSE para más detalles.

---

## Contacto

Para dudas o soporte, contacta a ferx096@gmail.com o abre un issue en GitHub.
