import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/../'))
import g_main

def test_vectore_storage_exists():
    assert hasattr(g_main, 'vectore_storage')
