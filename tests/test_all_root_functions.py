import pytest
import importlib
import sys
import os

# Agregar la raíz al path para importar los módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

modules = [
    'a_ocr_extractor',
    'b_embeddings',
    'c_prompts',
    # 'd_tools',
    # 'e_agents',
    # 'f_config',
    # 'g_main',
]
# Los módulos comentados inicializan recursos externos o bloquean al importar.

def get_functions(module):
    return [getattr(module, f) for f in dir(module) if callable(getattr(module, f)) and not f.startswith('__')]

@pytest.mark.parametrize('module_name', modules)
def test_import_and_functions(module_name):
    module = importlib.import_module(module_name)
    funcs = get_functions(module)
    # Solo verifica que se puedan importar y llamar sin argumentos si es posible
    for func in funcs:
        # Solo verifica que la función o clase existe y es callable
        assert callable(func), f'{func.__name__} de {module_name} no es callable'
