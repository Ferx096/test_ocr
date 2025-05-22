from dotenv import load_dotenv
import pandas as pd
import logging
import os
import re
import json
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.graph.message import add_messages
from langgraph.types import Command
from typing import Annotated, TypedDict, Literal, Dict, Optional, Union
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage
from a_embeddings_ocr import search_vectorestore
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from b_prompts import prompt_extract_company
from b_prompts import prompt_balance_sheet
from b_prompts import prompt_total_balance
from langchain_core.prompts import ChatPromptTemplate
from b_prompts import prompt_income_statement
import openpyxl


load_dotenv()
# configuracion de logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ======================================
# CARGAR DATOS
# ======================================
# llm
llm = AzureChatOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("OPENAI_API_VERSION"),
    deployment_name=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
    model_name="gpt-4",
)

logger.info(f"Azure LLM cargado")

embedding = AzureOpenAIEmbeddings(
    api_version=os.getenv("OPENAI_EMBEDDING_API_VERSION"),
    deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    model="text-embedding-3-large",
)
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

    messages: Optional[Annotated[list[HumanMessage], add_messages]]
    nombre_compañia: Optional[str]
    rut_compañia: Optional[str]
    fecha_reporte: Optional[str]
    creacion_report: Optional[dict]
    balance_general: Optional[dict]
    next: Optional[str]


import pathlib

def pdf_content():
    PDF_PATH = os.getenv("PDF_PATH", str(pathlib.Path(__file__).parent / "document" / "estados_financieros__pdf_93834000_202403.pdf"))
    if not os.path.exists(PDF_PATH):
        logger.error(f"No se encontró el archivo PDF: {PDF_PATH}")
        raise FileNotFoundError(f"No se encontró el archivo PDF: {PDF_PATH}")
    with open(PDF_PATH, "rb") as f:
        pdf_content = f.read()
    return pdf_content

from a_embeddings_ocr import save_faiss_index, load_faiss_index
from a_embeddings_ocr import get_embedding

import pathlib

FAISS_INDEX_PATH = str(pathlib.Path(__file__).parent / "faiss_index")

vectore_storage = None
embedding = get_embedding()

if os.path.exists(FAISS_INDEX_PATH):
    vectore_store = load_faiss_index(FAISS_INDEX_PATH, embedding)
    vectore_storage = vectore_store.as_retriever()
    logger.info(f"Vector store cargado desde cache {FAISS_INDEX_PATH}")
else:
    pdf_content_data = pdf_content()
    vectore_store = search_vectorestore(pdf_content_data)
    if vectore_store is not None:
        logger.info(f"Guardando FAISS index en {FAISS_INDEX_PATH} ...")
        try:
            save_faiss_index(vectore_store, FAISS_INDEX_PATH)
            logger.info(f"FAISS index guardado exitosamente en {FAISS_INDEX_PATH}")
            vectore_storage = vectore_store.as_retriever()
            logger.info(f"Almacenamiento de vectores listo y cacheado en {FAISS_INDEX_PATH}")
        except Exception as e:
            import traceback
            logger.error(f"Error al guardar FAISS index o crear el retriever: {e}")
            logger.error(traceback.format_exc())
            vectore_storage = None
        # Fin try/except

    else:
        logger.error("No se pudo crear el vector store, abortando inicialización.")
        vectore_storage = None


prompt_extract_company = prompt_extract_company
prompt_balance_sheet = prompt_balance_sheet
prompt_total_balance = prompt_total_balance
prompt_income_statement = prompt_income_statement


# ======================================
# AGENT COMPANY INFO
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
    """
    Extrae informacion del valor del texto corrigiendo valores innecesarios.
    Si el texto es un JSON válido, lo parsea directamente.
    Si no, intenta extraer los campos por regex y, como fallback, busca patrones alternativos.
    """
    # Intentar parsear como JSON primero
    try:
        data = json.loads(response_text)
        # Si es un dict y tiene los campos, devolverlos
        if isinstance(data, dict):
            return {
                "company_name": data.get("company_name") or data.get("nombre") or None,
                "company_rut": data.get("company_rut") or data.get("rut") or None,
                "report_date": data.get("report_date") or data.get("fecha") or None,
            }
    except Exception:
        pass

    # Regex principal
    name_match = re.search(r"Nombre.*?:\s*([\w\s\.,\-]+)", response_text, re.IGNORECASE)
    rut_match = re.search(r"RUT:?\s*([\d\-\.]+)", response_text, re.IGNORECASE)
    date_match = re.search(r"Fecha.*?:\s*([0-9]{2,4}[\/\-][0-9]{2,4}[\/\-][0-9]{2,4}|[0-9]{8})", response_text, re.IGNORECASE)

    # Fallbacks alternativos
    if not name_match:
        name_match = re.search(r"company_name\s*[:=]\s*['\"]?([\w\s\.,\-]+)['\"]?", response_text, re.IGNORECASE)
    if not rut_match:
        rut_match = re.search(r"company_rut\s*[:=]\s*['\"]?([\d\-\.]+)['\"]?", response_text, re.IGNORECASE)
    if not date_match:
        date_match = re.search(r"report_date\s*[:=]\s*['\"]?([0-9]{8}|[0-9]{2,4}[\/\-][0-9]{2,4}[\/\-][0-9]{2,4})['\"]?", response_text, re.IGNORECASE)

    # Si sigue sin datos, buscar la primera fecha y rut que aparezca
    if not rut_match:
        rut_match = re.search(r"[\d]{7,10}-[\dkK]", response_text)
    if not date_match:
        date_match = re.search(r"[0-9]{8}", response_text)

    return {
        "company_name": name_match.group(1).strip() if name_match else None,
        "company_rut": (
            rut_match.group(1).strip().replace(".", "").replace("-", "").replace(" ", "") if rut_match else None
        ),
        "report_date": date_match.group(1).strip() if date_match else None,
    }

def fallback_parse_company_info(text: str) -> dict:
    """
    Fallback: Busca patrones muy flexibles para nombre, rut y fecha en texto plano.
    """
    # Nombre: primera línea larga en mayúsculas sin símbolos o la primera línea significativa
    lines = text.splitlines()
    name = None
    for line in lines:
        l = line.strip()
        if len(l) > 5 and l.isupper() and not any(c in l for c in '0123456789:|*'):
            name = l
            break
    if not name:
        # Si no hay línea en mayúsculas, tomar la primera línea significativa
        for line in lines:
            l = line.strip()
            if len(l) > 5 and not any(c in l for c in '0123456789:|*'):
                name = l
                break
    # Fecha: cualquier fecha tipo dd/mm/yyyy, dd-mm-yyyy, yyyymmdd
    date = None
    for pat in [r"(\d{2}[/-]\d{2}[/-]\d{4})", r"(\d{4}[/-]\d{2}[/-]\d{2})", r"(\d{8})"]:
        m = re.search(pat, text)
        if m:
            date = m.group(1)
            break
    # RUT: cualquier número largo con guion
    rut = None
    m = re.search(r"(\d{7,10}-[\dkK])", text)
    if m:
        rut = m.group(1)
    return {"company_name": name, "company_rut": rut, "report_date": date}
def fallback_parse_balance_totals(text: str) -> dict:
    """
    Busca en el texto líneas con 'total activos', 'total pasivos', 'total patrimonio' y extrae el número asociado.
    """
    import re
    def find_total(label):
        pat = rf"{label}[^\d]*(\d[\d\.,]*)"
        m = re.search(pat, text, re.IGNORECASE)
        if m and m.group(1):
            return m.group(1).replace('.', '').replace(',', '')
        return None
    return {
        "total_activos": find_total("total[\s_]*activos"),
        "total_pasivos": find_total("total[\s_]*pasivos"),

def extract_account_values_from_text(text: str, cuentas_dict: dict) -> dict:
    """
    Para cada campo null en cuentas_dict, busca en el texto una línea que contenga el nombre de la cuenta y extrae el número asociado.
    Devuelve un nuevo dict con los valores encontrados (mantiene los existentes si no son null).
    """
    import re
    def normalize_key(key):
        return key.replace('_', ' ').replace('y', 'y').replace('de', '').replace('del', '').replace('la', '').replace('el', '').strip()
    result = {}
    for k, v in cuentas_dict.items():
        if v is not None:
            result[k] = v
            continue
        # Generar variantes del nombre de la cuenta
        nombre = normalize_key(k)
        # Buscar línea que contenga el nombre (case insensitive)
        pattern = re.compile(rf"{nombre}.*?(\(?-?\d[\d\.,]*\)?)", re.IGNORECASE)
        m = pattern.search(text)
        if m:
            num = m.group(1)
            # Limpiar número: quitar paréntesis (negativo), puntos, comas
            negativo = False
            if num.startswith('(') and num.endswith(')'):
                negativo = True
                num = num[1:-1]
            num = num.replace('.', '').replace(',', '')
            try:
                val = int(num)
                if negativo:
                    val = -val
                result[k] = val
            except Exception:
                result[k] = None
        else:
            result[k] = None
    return result

        "total_patrimonio": find_total("total[\s_]*patrimonio|patrimonio[\s_]*total")
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
            if "millon" in valor or "millones" in valor or "mill" in valor:
                number *= 1000000
            elif "mil" in valor:
                number *= 1000
            return number
    except Exception:
        return None


# Sumar valores en caso no exista suma:
def sum_group(grupo: Dict[str, str]) -> float:
    """Suma los valores numéricos de un grupo de cuentas."""
    return sum(parse_number(e) for e in grupo.values())


# agente
agent_balance_sheet = create_react_agent(
    llm, tools=[extract_balance_sheet], prompt=prompt_balance_sheet
)
prompt_total_balance_runnable = ChatPromptTemplate.from_template(prompt_total_balance)



# evaluador de balance total
def evaluate_balance_totals(llm, texto_balance: str):
    """
    Evalua la respuesta obtenida por el primer agente (el que obtiene el balance)
    En la evaluacion verifica si existe los totales o tiene que geerar su suma
    """
    chain = prompt_total_balance_runnable | llm | StrOutputParser()
    # El prompt espera la variable 'texto_balance', que debe ser un JSON string
    # Si texto_balance es un dict, serializarlo
    if isinstance(texto_balance, dict):
        texto_balance_str = json.dumps(texto_balance, ensure_ascii=False)
    else:
        texto_balance_str = texto_balance
    return chain.invoke({"texto_balance": texto_balance_str})


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


# Se usara el mismo parse_number pde balance general

# agente de balance de resultados
agent_income_statement = create_react_agent(
    llm, tools=[extract_income_statement], prompt=prompt_income_statement
)
