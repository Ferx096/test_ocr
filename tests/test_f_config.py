import pytest
from f_config import get_llm, get_embedding

def test_get_llm():
    llm = get_llm()
    assert llm is not None

def test_get_embedding():
    embedding = get_embedding()
    assert embedding is not None
