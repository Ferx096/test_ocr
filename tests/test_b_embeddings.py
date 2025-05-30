import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/../'))
import b_embeddings

def test_embeddings_guia_exists():
    assert hasattr(b_embeddings, 'embeddings_guia')

def test_search_vectorestore_exists():
    assert hasattr(b_embeddings, 'search_vectorestore')
