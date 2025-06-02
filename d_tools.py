import logging
import sys
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from rapidfuzz import fuzz
import pandas as pd

def find_matches_in_ocr(ocr_text, guide_docs, embedding=None, threshold_fuzzy=80, threshold_semantic=0.80, top_k=2):
    """
    Matching semántico (embeddings) + fuzzy + extracción robusta de valores.
    Args:
        ocr_text (str): Texto OCR del PDF.
        guide_docs (List[Document]): Chunks de la guía financiera.
        embedding: Modelo de embedding (obligatorio para semántica).
        threshold_fuzzy (int): Umbral fuzzy mínimo para aceptar match.
        threshold_semantic (float): Umbral de similitud semántica (coseno) mínimo.
        top_k (int): Número de matches semánticos a considerar por línea.
    Returns:
        List[dict]: Matches de calidad con variable, valor y contexto.
    """
    from langchain_community.vectorstores import FAISS
    import numpy as np
    import re
    # 1. Construir vectorstore de la guía
    vectordb = FAISS.from_documents(guide_docs, embedding)
    # 2. Procesar OCR en líneas
    ocr_lines = [line.strip() for line in ocr_text.split('\n') if line.strip()]
    results = []
    seen = set()
    for line in ocr_lines:
        for doc in guide_docs:
            guia_chunk = doc.page_content
            # Fallback robusto para chunks cortos (e.g. CAJA, BANCOS)
            if len(guia_chunk) <= 6:
                import unicodedata
                def normalize(text):
                    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
                    return ''.join(c for c in text.lower() if c.isalnum())
                guia_norm = normalize(guia_chunk)
                # Extraer prefijo antes del primer número para comparar solo el nombre
                line_prefix = line
                m = re.match(r'([^\d-]+)', line)
                if m:
                    line_prefix = m.group(1)
                line_norm = normalize(line_prefix)
                fuzzy_score = fuzz.ratio(guia_norm, line_norm)
                if fuzzy_score >= 70:
                    sim = 1.0
                    # Extracción de valor para fallback
                    value = None
                    value_match = re.search(r'(-?\d{1,3}(?:[.,]\d{3})*(?:[.,]\d+)?|\d+)', line)
                    if value_match:
                        raw = value_match.group(1)
                        norm = raw.replace('.', '').replace(',', '.') if raw.count(',') else raw.replace(',', '')
                        try:
                            value = float(norm)
                            if '-' in raw.strip():
                                value = -abs(value)
                        except Exception:
                            value = None
                    key = (guia_chunk.strip().lower(), line.strip().lower())
                    if key not in seen:
                        seen.add(key)
                        results.append({
                        'guia_chunk': guia_chunk,
                        'ocr_line': line,
                        'semantic_score': sim,
                        'fuzzy_score': fuzzy_score,
                        'value': value
                    })
                continue
    print('[DEBUG] results before dedup:', results)
    # DEBUG: print all ocr_lines and guide_docs for inspection
    print('[DEBUG] ocr_lines:', ocr_lines)
    print('[DEBUG] guide_docs:', [doc.page_content for doc in guide_docs])
    # 7. Deduplicar: solo el mejor match por guia_chunk
    best_by_chunk = {}
    for r in results:
        key = r['guia_chunk'].strip().lower()
        if key not in best_by_chunk or r['fuzzy_score'] > best_by_chunk[key]['fuzzy_score']:
            best_by_chunk[key] = r
        # DEBUG: print all results for inspection
    # Para chunks cortos, aceptar fuzzy_score >= 70 aunque no sea 100
    filtered = []
    for r in best_by_chunk.values():
        if r['value'] is not None or r['value'] == 0:
            if len(r['guia_chunk']) <= 6 and r['fuzzy_score'] >= 70:
                filtered.append(r)
            elif r['fuzzy_score'] == 100 or (r['semantic_score'] >= threshold_semantic and r['fuzzy_score'] >= threshold_fuzzy):
                filtered.append(r)
    return filtered
    # DEBUG: print filtered for inspection
    print('[DEBUG] filtered:', filtered)
    return filtered
import json
import re
from dotenv import load_dotenv
from typing import Dict
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from typing import Optional, Annotated
from typing_extensions import TypedDict
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from b_embeddings import search_vectorestore
from c_prompts import prompt_extract_company, prompt_balance_sheet, prompt_total_balance, prompt_income_statement
from f_config import get_llm
from f_config import get_embedding


import sys
if 'pytest' in sys.modules:

    class DummyEmbedding:
        pass
    from unittest.mock import MagicMock
    llm = MagicMock()
    embedding = DummyEmbedding()
else:
    load_dotenv()
    # configuracion de logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger(__name__)
    # llm
    llm = get_llm()
    logger.info(f"Azure LLM cargado")
    embedding = get_embedding()
    logger.info(f"Azure embedding cargado")

# ======================================
# PROMPT + ESTRUCTURA
# ======================================
"""
Se pretende crear 3 agentes jerargicos para obtener informacion valiosa
1. Agente info de empresa(tool info y prompt):
    agente encargado de obtener informacion de una empresa de un archivo de embedding
2. Agente variables financieros(tool- funcion):
    agente encaragdo de obtener informacion financiera; valor - numero
3. Agente verificador (tool-condicion)
    agente encargado de regular la  respuesta y marcarlo como ok o regreso
"""


class State(TypedDict):
    """Estructura de estado compartido entre agentes"""
    messages: Optional[list[HumanMessage]]
    nombre_compañia: Optional[str]
    rut_compañia: Optional[str]
    fecha_reporte: Optional[str]
    creacion_report: Optional[dict]
    balance_general: Optional[dict]
    next: Optional[str]
    excel_bytes: Optional[bytes]

#almacenamiento de vectores
#prompt
prompt_extract_company = prompt_extract_company
prompt_balance_sheet = prompt_balance_sheet
prompt_total_balance = prompt_total_balance
prompt_income_statement = prompt_income_statement


# ======================================
# TOOLS COMPANY INFO
# ======================================
# crear tool de company info
@tool
def extract_company_info(query: str) -> str:
    """
    Extrae informacion de la empresa desde vector store
    """
    results = vectore_storage.invoke(query)
    return "\n".join([doc.page_content for doc in results])


# agente


# funcion para extraer informacion del texto del agente
def parse_company_info(response_text: str) -> dict:
    """Extrae informacion del valor del texto corrigiendo  valores innecesarios"""
    name_match = re.search(r"Nombre.*?:\s*(.+)", response_text, re.IGNORECASE)
    rut_match = re.search(r"RUT:?\s*([\d\-\.]+)", response_text, re.IGNORECASE)
    date_match = re.search(
        r"Fecha.*?:\s*([0-9]/[0-9]/[0-9])", response_text, re.IGNORECASE
    )

    return {
        "company_name": name_match.group(1).strip() if name_match else None,
        "company_rut": (
            rut_match.group(1)
            .strip()
            .replace(".", "")
            .replace("-", "")
            .replace(" ", "")
            .replace(",", "")
            .replace("*", "")
            .replace("'", "")
            .replace('"', "")
            if rut_match
            else None
        ),
        "report_date": date_match.group(1).strip() if date_match else None,
    }


# ======================================
# TOOL + FUNCTION BALANCE GENERAL
# ======================================
# crear tool de balance general
@tool
def extract_balance_sheet(query: str) -> str:
    """
    Extrae datos del balance general de la empresa del vectore storage.
    Dividiendo la inforamcion extraida en activos, pasivos y patrimonio
    """
    results = vectore_storage.invoke(query)
    return "\n".join([doc.page_content for doc in results])


# funcion para asegurarnos que los valores no tengan string
def parse_number(valor):
    """
    Convierte strings como mil y millon a float
    Retorna None si no puede convertir.
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
            if "mil" in valor:
                number *= 1000
            elif "mill" in valor or "millon" in valor:
                number *= 1000000
            return number
    except Exception:
        return None

# Sumar valores en caso no exista suma:
def sum_group(grupo: Dict[str, str]) -> float:
    """Suma los valores numéricos de un grupo de cuentas."""
    return sum(parse_number(e) for e in grupo.values())
# evaluador de balance total
from langchain_core.prompts import ChatPromptTemplate
prompt_total_balance_runneable = ChatPromptTemplate.from_template(prompt_total_balance)

def evaluate_balance_totals(llm, texto_balance, prompt_total_balance_runneable):
    """
    Evalua la respuesta obtenida por el primer agente (el que obtiene el balance)
    En la evaluacion verifica si existe los totales o tiene que geerar su suma
    """
    chain = prompt_total_balance_runneable | llm | StrOutputParser()
    if isinstance(texto_balance, dict):
        texto_balance_str = json.dumps(texto_balance, ensure_ascii=False)
    else:
        texto_balance_str = texto_balance
    return chain.invoke({"balance_texto": texto_balance_str})





# ======================================
# TOOL + FUNCTIONS ESTADO DE RESULTADOS
# ======================================
# Herramienta para extraer informacion de estado de resultaddos de la empresa
@tool
def extract_income_statement(query: str) -> str:
    """
    Extrae datos de estado de resultados de la empresa del vectore storage.
    Dividiendo la inforamcion extraida en
    """
    results = vectore_storage.invoke(query)
    return "\n".join([doc.page_content for doc in results])

# Se usara el mismo parse_number pdf balance general
# agente de balance de resultados

from rapidfuzz import fuzz
from typing import List
from langchain.schema import Document

def find_matches_in_ocr(ocr_text: str, guide_docs: List[Document], embedding=None, threshold_fuzzy=70, threshold_semantic=0.5, top_k=1):
    """
    Busca matches entre líneas del OCR y los ítems individuales de la guía usando fuzzy y (opcional) similitud semántica.
    Extrae valores numéricos asociados y retorna lista de dicts con match y valor.
    """
    ocr_lines = [l.strip() for l in ocr_text.split("\n") if l.strip()]
    results = []
    # Extraer ítems individuales de la guía
    guide_items = []
    for doc in guide_docs:
        for line in doc.page_content.split("\n"):
            item = line.strip().lstrip('-').strip()
            if item and not item.startswith('#'):
                guide_items.append(item)
    for guia_item in guide_items:
        best_score = 0
        best_line = None
        for line in ocr_lines:
            score = fuzz.token_set_ratio(guia_item, line)
            if score > best_score:
                best_score = score
                best_line = line
        if best_score >= threshold_fuzzy:
            match = re.search(r"([\d\.\,]+)", best_line)
            try:
                value = float(match.group(1).replace('.', '').replace(',', '.')) if match else None
            except Exception:
                value = None
            results.append({
                'guia_chunk': guia_item,
                'ocr_line': best_line,
                'score': best_score,
                'value': value
            })
    results = [r for r in results if r['value'] is not None]
    return results

# Exportar la función para los tests
__all__ = ['find_matches_in_ocr']


def ensure_totals(resultados):
    """
    Agrupa los resultados en activos, pasivos y patrimonio usando un mapeo explícito de cuentas.
    Si no existe el total en el grupo, lo calcula y lo agrega.
    """
    # Diccionario de mapeo robusto: nombre de cuenta (lower) -> grupo
    mapeo = {
        'caja y bancos': 'activo',
        'caja': 'activo',
        'bancos': 'activo',
        'efectivo': 'activo',
        'cuentas por cobrar': 'activo',
        'inventarios': 'activo',
        'total activos': 'activo',
        'deuda financiera': 'pasivo',
        'proveedores': 'pasivo',
        'cuentas por pagar': 'pasivo',
        'total pasivos': 'pasivo',
        'capital social': 'patrimonio',
        'utilidades retenidas': 'patrimonio',
        'total patrimonio': 'patrimonio',
        'patrimonio neto': 'patrimonio',
        'flujo de caja': 'activo',
        # Agrega aquí más mapeos según tu guía real
    }
    # Agrupar resultados
    grupos = {'activo': [], 'pasivo': [], 'patrimonio': []}
    otros = []
    for r in resultados:
        nombre = r.get('guia_chunk', '').strip().lower()
        grupo = None
        for clave, tipo in mapeo.items():
            if clave in nombre:
                grupo = tipo
                break
        if grupo:
            grupos[grupo].append(r)
        else:
            otros.append(r)
    # Calcular totales si no existen
    nuevos_resultados = resultados.copy()
    for grupo, items in grupos.items():
        if not items:
            continue
        # Buscar si ya existe un total explícito
        tiene_total = any('total' in r['guia_chunk'].lower() for r in items)
        if not tiene_total:
            suma = sum(r['value'] for r in items if isinstance(r['value'], (int, float)))
            nuevos_resultados.append({
                'guia_chunk': f'Total {grupo}s',
                'ocr_line': '',
                'value': suma
            })
    return nuevos_resultados


def exportar_a_excel(resultados, nombre_archivo="resultado.xlsx"):
    """
    Exporta la lista de resultados a un archivo Excel con columnas: Cuenta, Valor.
    """
    import pandas as pd
    filas = []
    for r in resultados:
        filas.append({
            'Cuenta': r.get('guia_chunk', ''),
            'Valor': r.get('value', '')
        })
    df = pd.DataFrame(filas)
    df.to_excel(nombre_archivo, index=False)
    return nombre_archivo

