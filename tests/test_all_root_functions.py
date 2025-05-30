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
    'd_tools',
    'e_agents',
    'f_config',
    'g_main',
]

def get_functions(module):
    return [getattr(module, f) for f in dir(module) if callable(getattr(module, f)) and not f.startswith('__')]

@pytest.mark.parametrize('module_name', modules)
def test_import_and_functions(module_name):
    module = importlib.import_module(module_name)
    funcs = get_functions(module)
    # Solo verifica que se puedan importar y llamar sin argumentos si es posible
    for func in funcs:
        try:
            # Intenta llamar funciones sin argumentos
            func()
        except TypeError:
            # Si requiere argumentos, ignora
            pass
        except Exception as e:
            # Si hay otro error, falla el test
            pytest.fail(f'Error en {func.__name__} de {module_name}: {e}')
