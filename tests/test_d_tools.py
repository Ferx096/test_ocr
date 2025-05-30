import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/../'))
import d_tools

def test_extract_company_info_exists():
    assert hasattr(d_tools, 'extract_company_info')

def test_parse_company_info_exists():
    assert hasattr(d_tools, 'parse_company_info')

def test_extract_balance_sheet_exists():
    assert hasattr(d_tools, 'extract_balance_sheet')

def test_parse_number_exists():
    assert hasattr(d_tools, 'parse_number')

def test_sum_group_exists():
    assert hasattr(d_tools, 'sum_group')

def test_extract_income_statement_exists():
    assert hasattr(d_tools, 'extract_income_statement')
