import pytest
import test

def test_main_runs():
    # Solo verifica que el script principal corre sin errores
    try:
        test.main()
    except Exception as e:
        pytest.fail(f"Fallo al ejecutar test.main(): {e}")
