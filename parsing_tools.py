"""
Funciones de parsing y utilidades numéricas para extracción financiera.
"""
import re
from typing import Dict

def parse_number(valor):
    """
    Convierte strings como "mil" y "millón" a float, o retorna None si no es posible.
    Intenta extraer el valor numérico de un string, considerando palabras como 'mil' y 'millón'.
    """
    try:
        if isinstance(valor, (int, float)):
            return valor
        if isinstance(valor, str):
            valor = valor.lower().replace(",", "")
            match = re.search(r"(\d+(?:\.\d+)?)", valor)
            if not match:
                return None
            number = float(match.group(1))
            if "millon" in valor or "millones" in valor or "mill" in valor:
                number *= 1000000
            elif "mil" in valor:
                number *= 1000
            return number
    except Exception:
        return None

def sum_group(grupo: Dict[str, str]) -> float:
    """
    Suma los valores numéricos de un grupo de cuentas (dict).
    """
    return sum(parse_number(e) for e in grupo.values())
