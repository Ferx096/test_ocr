"""
Funciones de preprocesamiento OCR: limpieza, segmentación y extracción de pares término-valor y tablas.
Incluye heurísticas para identificar líneas relevantes y debugging de resultados.
"""
import re
import unicodedata

def clean_ocr_text(text):
    """
    Normaliza y limpia el texto OCR, eliminando caracteres extraños y espacios innecesarios.
    Args:
        text (str): Texto crudo extraído por OCR.
    Returns:
        str: Texto limpio y normalizado.
    """
    # Normaliza unicode, quita caracteres raros, corrige espacios
    """
    Divide el texto en líneas normales y posibles tablas, usando heurísticas de separación.
    Args:
        text (str): Texto limpio.
    Returns:
        tuple: (normal_lines, tables) listas de líneas normales y de tablas.
    """
    text = unicodedata.normalize('NFKC', text)
    text = re.sub(r'[\x00-\x1F\x7F]+', ' ', text)  # quita caracteres de control
    text = re.sub(r'\s+', ' ', text)
    text = text.replace('\u200b', '')
    return text.strip()
    """
    Preprocesa el resultado OCR, limpiando el texto y extrayendo líneas y tablas.
    Args:
        ocr_result (dict): Diccionario con claves 'full_text' y 'tables_data'.
    Returns:
        dict: Diccionario con listas de líneas, tablas y texto crudo limpio.
    """
    Realiza limpieza avanzada y segmentación de texto OCR, dividiéndolo en líneas útiles.
    Args:
        text (str): Texto OCR limpio.
    Returns:
        list: Lista de líneas segmentadas y fusionadas.
    """
    """

def extract_lines_and_tables(text):
    # Divide en líneas y detecta posibles tablas (líneas con muchos espacios o separadores)
    lines = text.split('\n')
    tables = []
    normal_lines = []
    """
    Extrae líneas candidatas a pares término-valor usando heurísticas simples.
    Args:
        text (str): Texto OCR limpio.
    Returns:
        list: Líneas candidatas a contener pares término-valor.
    """
    for line in lines:
        if re.search(r'(\s{2,}|\||;|,\s)', line):
            tables.append(line)
        else:
    """
    Busca y extrae pares término-valor en bloques de texto, usando patrones regulares.
    Args:
        text (str): Texto OCR limpio.
    Returns:
        list: Lista de tuplas (término, [valores]).
    """
            normal_lines.append(line)
    return normal_lines, tables

def preprocess_ocr_result(ocr_result):
    # Espera un dict con 'full_text' y 'tables_data'
    text = ocr_result.get('full_text', '')
    text = clean_ocr_text(text)
    lines, tables = extract_lines_and_tables(text)
    return {'lines': lines, 'tables': tables, 'raw': text}
def preprocess_ocr_text(text):
    """
    Extrae filas de tabla detectando líneas con múltiples números grandes.
    Args:
        text (str): Texto OCR limpio.
    Returns:
        list: Listas de columnas por fila de tabla.
    """
    # Limpieza avanzada y segmentación
    import re
    text = re.sub(r'\s+', ' ', text)
    lines = re.split(r' {3,}|\n', text)
    lines = [l.strip() for l in lines if l.strip()]
    merged = []
    """
    Extrae pares término-valor de cualquier línea con palabra y número grande.
    Args:
        text (str): Texto OCR limpio.
    Returns:
        list: Lista de tuplas (término, valor).
    """
    for line in lines:
        if merged and (merged[-1][-1].isdigit() or merged[-1][-1] in ".,;:") and (line[0].islower() or line[0].isdigit()):
            merged[-1] += ' ' + line
        else:
            merged.append(line)
    return merged

    """
    Guarda líneas que no matchean ningún regex de término-valor para debugging.
    Args:
        text (str): Texto OCR limpio.
        regexes (list): Lista de patrones regex.
        out_path (str): Ruta de archivo de salida.
    """
def extract_term_value_candidates(text):
    # Extrae líneas candidatas a pares término-valor usando heurísticas
    import re
    candidates = []
    for line in re.split(r'\n| {2,}', text):
        line = line.strip()
        # Heurística: línea con texto y número grande al final
        if re.search(r'[a-zA-Z].*\d{3,}[\.,]?\d*$', line):
            candidates.append(line)
    """
    Extrae pares término-valor agrupando líneas: término en una línea, valores numéricos en las siguientes.
    Args:
        text (str): Texto OCR limpio.
    Returns:
        list: Lista de tuplas (término, [valores]).
    """
    return candidates

def extract_term_value_pairs(text):
    # Busca pares término-valor en bloques de texto (balance)
    import re
    pairs = []
    # Busca líneas con patrón: texto ... número(s)
    for line in re.split(r'\n| {2,}', text):
        line = line.strip()
        # Busca patrón: término (palabras) + uno o más números grandes
        m = re.match(r'([\w\s\(\)\-\.]+?)\s+([\d\.\,\(\)\-]+)(\s+[\d\.\,\(\)\-]+)*$', line)
        if m:
            # Extrae término y todos los valores numéricos al final
            term = m.group(1).strip()
            nums = re.findall(r'[\d\.\,\(\)\-]+', line[len(term):])
            if nums:
                pairs.append((term, nums))
    return pairs

def extract_table_rows(text):
    # Extrae filas de tabla por alineación de espacios (balance)
    import re
    rows = []
    for line in text.split('\n'):
        # Busca líneas con al menos dos números grandes
        if len(re.findall(r'\d{3,}', line)) >= 2:
    """
    Guarda candidatos multilineales para debugging, mostrando términos y líneas siguientes.
    Args:
        text (str): Texto OCR limpio.
        out_path (str): Ruta de archivo de salida.
    """
            # Divide por 2+ espacios o tabulador
            cols = re.split(r' {2,}|\t', line.strip())
            if len(cols) >= 2:
                rows.append(cols)
    return rows
    """
    Busca patrones de término + nota + valor1 + valor2 en líneas largas.
    Args:
        text (str): Texto OCR limpio.
    Returns:
        list: Lista de tuplas (término, nota, valor1, valor2).
    """

def extract_flexible_term_value_pairs(text):
    # Extrae pares término-valor de cualquier línea con palabra y número grande
    import re
    pairs = []
    for line in text.split('\n'):
        line = line.strip()
        # Busca cualquier línea con palabra y número grande (en cualquier parte)
        m = re.search(r'([A-Za-zÁÉÍÓÚáéíóúñÑ\(\)\-\s\.]+?)(\d{3,}[\.,]?\d*)', line)
        if m:
            term = m.group(1).strip()
            value = m.group(2).strip()
            if term and value:
                pairs.append((term, value))
    return pairs
def debug_failed_lines(text, regexes, out_path="ocr_debug_failed_lines.txt"):
    """Guarda líneas que no matchean ningún regex de término-valor."""
    with open(out_path, "w", encoding="utf-8") as f:
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
            matched = False
            for rx in regexes:
                if re.match(rx, line):
                    matched = True
                    break
            if not matched:
                f.write(line + "\n")


def extract_multiline_term_value_pairs(text):
    # Extrae pares término-valor agrupando líneas: término en una línea, valores numéricos en las siguientes
    import re
    pairs = []
    lines = text.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        # Si la línea es texto (contiene letras y no es solo número)
        if re.search(r'[A-Za-zÁÉÍÓÚáéíóúñÑ]', line) and not re.match(r'^\d+[\d\.,]*$', line):
            term = line
            values = []
            j = i + 1
            # Si la siguiente línea es un número pequeño (nota), saltar
            if j < len(lines) and re.match(r'^\d{1,2}$', lines[j].strip()):
                j += 1
            # Ahora buscar hasta 3 líneas numéricas grandes
            num_found = 0
            while j < len(lines) and num_found < 3:
                num_line = lines[j].strip()
                if re.match(r'^[\d\.,\(\)\-\+\s]{5,}$', num_line):
                    values.append(num_line)
                    num_found += 1
                    j += 1
                else:
                    break
            if values:
                pairs.append((term, values))
            i = j
        else:
            i += 1
    return pairs

def debug_multiline_candidates(text, out_path="ocr_debug_multiline_candidates.txt"):
    import re
    lines = text.split('\n')
    with open(out_path, "w", encoding="utf-8") as f:
        for i, line in enumerate(lines):
            if re.search(r'[A-Za-zÁÉÍÓÚáéíóúñÑ]', line) and not re.match(r'^\d+[\d\.,]*$', line):
                f.write(f"Término: {line}\n")
                for j in range(1, 4):
                    if i + j < len(lines):
                        f.write(f"  Siguiente: {lines[i+j]}\n")

def extract_flatline_term_value_groups(text):
    # Busca patrones de término + nota + valor1 + valor2 en líneas largas
    import re
    pattern = re.compile(r'([A-Za-zÁÉÍÓÚáéíóúñÑ\s]+)\s+(\d{1,2})\s+([\d\.,]{5,})\s+([\d\.,]{5,})')
    results = []
    for match in pattern.finditer(text):
        term = match.group(1).strip()
        nota = match.group(2).strip()
        val1 = match.group(3).strip()
        val2 = match.group(4).strip()
        results.append((term, nota, val1, val2))
    return results

