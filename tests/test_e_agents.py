import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/../'))
import e_agents

def test_module_import():
    assert e_agents is not None
