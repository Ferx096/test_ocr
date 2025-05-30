import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/../'))
import c_prompts

def test_prompt_extract_company_exists():
    assert hasattr(c_prompts, 'prompt_extract_company')

def test_prompt_balance_sheet_exists():
    assert hasattr(c_prompts, 'prompt_balance_sheet')

def test_prompt_total_balance_exists():
    assert hasattr(c_prompts, 'prompt_total_balance')

def test_prompt_income_statement_exists():
    assert hasattr(c_prompts, 'prompt_income_statement')
