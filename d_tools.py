import logging
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
        # 3. Buscar top_k matches semánticos
        docs_and_scores = vectordb.similarity_search_with_score(line, k=top_k)
        for doc, score in docs_and_scores:
            # FAISS devuelve menor distancia = más similar; convertir a similitud coseno
            sim = 1 - score if score <= 1 else 1/(1+score)
            if sim < threshold_semantic:
                continue
            guia_chunk = doc.page_content
            # 4. Fuzzy adicional para refinar
            fuzzy_score = fuzz.token_set_ratio(guia_chunk.lower(), line.lower())
            if fuzzy_score < threshold_fuzzy:
                continue
            # 5. Extracción robusta de valores numéricos (regex, normalización)
            value = None
            value_match = re.search(r'([-+]?[0-9]{1,3}(?:[.,][0-9]{3})*(?:[.,][0-9]+)?)', line)
            if value_match:
                raw = value_match.group(1)
                norm = raw.replace('.', '').replace(',', '.') if raw.count(',') else raw.replace(',', '')
                try:
                    value = float(norm)
                except Exception:
                    value = None
            # 6. Validación de duplicados/contexto
            key = (guia_chunk.strip().lower(), line.strip().lower())
            if key in seen:
                continue
            seen.add(key)
            results.append({
                'guia_chunk': guia_chunk,
                'ocr_line': line,
                'semantic_score': round(sim, 3),
                'fuzzy_score': fuzzy_score,
                'value': value
            })
    # 7. Filtrar por calidad mínima (ejemplo: ambos scores altos y valor extraído)
    filtered = [r for r in results if r['semantic_score'] >= threshold_semantic and r['fuzzy_score'] >= threshold_fuzzy and r['value'] is not None]
    return filtered

import json
import re
from dotenv import load_dotenv
from typing import Dict
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from typing import Optional, Annotated
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.prebuilt import create_react_agent
from b_embeddings import search_vectorestore
from c_prompts import prompt_extract_company, prompt_balance_sheet, prompt_total_balance, prompt_income_statement
from f_config import get_llm
from f_config import get_embedding
from g_main import vectore_storage


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
    messages: Annotated[Optional[list[HumanMessage]], add_messages]
    nombre_compañia: Optional[str]
    rut_compañia: Optional[str]
    fecha_reporte: Optional[str]
    creacion_report: Optional[dict]
    balance_general: Optional[dict]
    next: Optional[str]
    excel_bytes: Optional[bytes]

#almacenamiento de vectores
vectore_storage = vectore_storage
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
agent_company_info = create_react_agent(
    llm,
    tools=[extract_company_info],
    prompt=prompt_extract_company,
)


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
# agente
agent_balance_sheet = create_react_agent(llm, tools=[extract_balance_sheet], prompt=prompt_balance_sheet)

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
agent_income_statement = create_react_agent(
    llm, tools=[extract_income_statement], prompt=prompt_income_statement
)
