"""
Funciones de preprocesamiento OCR: limpieza, segmentación y extracción de pares término-valor y tablas.
Incluye heurísticas para identificar líneas relevantes y debugging de resultados.
import logging
# Centralización de patrones regex para fácil ajuste
REGEX_TABLE = r'(\s{2,}|\||;|,\s)'
REGEX_TERM_VALUE = r'[a-zA-Z].*\d{3,}[\.,]?\d*$'
REGEX_NUMERIC = r'[\d\.\,\(\)\-]+'

from utils_logging import setup_logger

logger = setup_logger("ocr_preprocess", "ocr_preprocess.log")

"""
import re
import unicodedata

def clean_ocr_text(text):
    """
    Normaliza y limpia el texto OCR, eliminando caracteres extraños y espacios innecesarios.
    Args:
        text (str): Texto crudo extraído por OCR.
    Returns:
        str: Texto limpio y normalizado.
    """
    if not isinstance(text, str):
        logger.warning(f"clean_ocr_text recibió un tipo inesperado: {type(text)}")
        return ""
    try:
        text = unicodedata.normalize('NFKC', text)
        text = re.sub(r'[\x00-\x1F\x7F]+', ' ', text)  # quita caracteres de control
        text = re.sub(r'\s+', ' ', text)
        text = text.replace('\u200b', '')
        return text.strip()
    except Exception as e:
        logger.error(f"Error en clean_ocr_text: {e}")
        return ""



def extract_lines_and_tables(text):
    # Divide en líneas y detecta posibles tablas (líneas con muchos espacios o separadores)
    """
    Divide el texto en líneas normales y posibles tablas, usando heurísticas de separación.
    Args:
        text (str): Texto limpio.
    Returns:
        tuple: (normal_lines, tables) listas de líneas normales y de tablas.
    """
    lines = text.split('\n')
    tables = []
    normal_lines = []
    
    for line in lines:
        if re.search(r'(\s{2,}|\||;|,\s)', line):
            tables.append(line)
        else:
 
            normal_lines.append(line)
    return normal_lines, tables

def preprocess_ocr_result(ocr_result):
    """
    Procesa el resultado OCR extrayendo texto limpio, líneas y tablas.
    Args:
        ocr_result (dict): Debe contener 'full_text' y opcionalmente 'tables_data'.
    Returns:
        dict: {'lines': líneas normales, 'tables': tablas, 'raw': texto limpio}
    """
    text = ocr_result.get('full_text', '')
    text = clean_ocr_text(text)
    lines, tables = extract_lines_and_tables(text)
    return {'lines': lines, 'tables': tables, 'raw': text}

def preprocess_ocr_text(text):
    """
    Extrae filas de tabla y pares término-valor usando heurísticas y regex.
    Args:
        text (str): Texto OCR limpio.
    Returns:
        list: Listas de columnas por fila de tabla o tuplas (término, valor).
    """
    # Limpieza avanzada y segmentación
    import re
    text = re.sub(r'\s+', ' ', text)
    lines = re.split(r' {3,}|\n', text)
    lines = [l.strip() for l in lines if l.strip()]
    merged = []

    for line in lines:
        if merged and (merged[-1][-1].isdigit() or merged[-1][-1] in ".,;:") and (line[0].islower() or line[0].isdigit()):
            merged[-1] += ' ' + line
        else:
            merged.append(line)
    return merged
