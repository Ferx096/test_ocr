import pytest
from ocr_preprocess import clean_ocr_text, extract_lines_and_tables, preprocess_ocr_result, preprocess_ocr_text, extract_term_value_candidates, extract_term_value_pairs, extract_table_rows, extract_flexible_term_value_pairs, debug_failed_lines, extract_multiline_term_value_pairs, debug_multiline_candidates, extract_flatline_term_value_groups

def test_clean_ocr_text():
    text = "Texto de prueba con errores 123"
    result = clean_ocr_text(text)
    assert isinstance(result, str)

def test_extract_lines_and_tables():
    text = "Línea 1\nLínea 2\nTabla: 1,2,3"
    result = extract_lines_and_tables(text)
    assert isinstance(result, tuple)

def test_preprocess_ocr_result():
    text = "Texto OCR"
    result = preprocess_ocr_result(text)
    assert isinstance(result, str)

def test_preprocess_ocr_text():
    text = "Texto OCR"
    result = preprocess_ocr_text(text)
    assert isinstance(result, str)

def test_extract_term_value_candidates():
    text = "Activo: 1000\nPasivo: 500"
    result = extract_term_value_candidates(text)
    assert isinstance(result, list)

def test_extract_term_value_pairs():
    text = "Activo: 1000\nPasivo: 500"
    result = extract_term_value_pairs(text)
    assert isinstance(result, list)

def test_extract_table_rows():
    text = "Fila1\nFila2"
    result = extract_table_rows(text)
    assert isinstance(result, list)

def test_extract_flexible_term_value_pairs():
    text = "Activo: 1000\nPasivo: 500"
    result = extract_flexible_term_value_pairs(text)
    assert isinstance(result, list)

def test_debug_failed_lines():
    text = "Línea fallida"
    regexes = []
    debug_failed_lines(text, regexes, out_path="ocr_debug_failed_lines.txt")
    assert True

def test_extract_multiline_term_value_pairs():
    text = "Activo: 1000\nPasivo: 500"
    result = extract_multiline_term_value_pairs(text)
    assert isinstance(result, list)

def test_debug_multiline_candidates():
    text = "Línea multilinea"
    debug_multiline_candidates(text, out_path="ocr_debug_multiline_candidates.txt")
    assert True

def test_extract_flatline_term_value_groups():
    text = "Activo: 1000\nPasivo: 500"
    result = extract_flatline_term_value_groups(text)
    assert isinstance(result, list)
