import pytest
from c_tools import parse_number, sum_group

def test_parse_number_int():
    assert parse_number(1000) == 1000

def test_parse_number_float():
    assert parse_number(1234.56) == 1234.56

def test_parse_number_str():
    assert parse_number("1,234") == 1234
    assert parse_number("2 mil") == 2000
    assert parse_number("3 millones") == 3000000
    assert parse_number("4 millon") == 4000000
    assert parse_number("5.5 mil") == 5500
    assert parse_number("6.5 mill") == 6500000
    assert parse_number("no es numero") is None

def test_sum_group():
    grupo = {"a": "1000", "b": "2 mil", "c": 3000}
    assert sum_group(grupo) == 1000 + 2000 + 3000
