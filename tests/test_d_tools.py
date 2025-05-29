import pytest
from d_tools import extract_company_info, parse_company_info, extract_balance_sheet, parse_number, sum_group, extract_income_statement

def test_extract_company_info():
    result = extract_company_info("empresa de prueba")
    assert isinstance(result, str)

def test_parse_company_info():
    response = extract_company_info("empresa de prueba")
    result = parse_company_info(response)
    assert isinstance(result, dict)

def test_extract_balance_sheet():
    result = extract_balance_sheet("balance de prueba")
    assert isinstance(result, str)

def test_parse_number():
    assert isinstance(parse_number("1000"), (int, float))

def test_sum_group():
    grupo = {"a": "100", "b": "200"}
    assert sum_group(grupo) == 300

def test_extract_income_statement():
    result = extract_income_statement("estado de resultados")
    assert isinstance(result, str)
