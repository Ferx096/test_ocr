import unicodedata
import re

SYNONYMS = {
    "activo": ["activos", "asset", "assets"],
    "pasivo": ["pasivos", "liability", "liabilities"],
    "patrimonio": ["equity", "capital", "patrimonio neto"]
}

def normalize_term(term):
    """
    Normaliza términos: minúsculas, sin acentos, sin caracteres especiales.
    Args:
        term (str): Término a normalizar.
    Returns:
        str: Término normalizado.
    Ejemplo:
        'Áctivo Fijo' -> 'activo fijo'
    """
    term = term.lower()
    term = ''.join(c for c in unicodedata.normalize('NFKD', term) if not unicodedata.combining(c))
    term = re.sub(r'[^a-z0-9 ]', '', term)
    return term.strip()

def normalize_category(cat):
    """
    Normaliza y categoriza usando sinónimos.
    Args:
        cat (str): Categoría a normalizar.
    Returns:
        str: Categoría estándar ('activo', 'pasivo', 'patrimonio', 'otros').
    """
    cat = normalize_term(cat)
    for key, values in SYNONYMS.items():
        if cat in values or key in cat:
            return key
    return "otros"
