import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/../'))
import f_config

def test_get_llm_exists():
    assert hasattr(f_config, 'get_llm')

def test_get_embedding_exists():
    assert hasattr(f_config, 'get_embedding')
