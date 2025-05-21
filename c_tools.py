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
from b_prompts import prompt_income_statement


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

def load_pdf_content():
    PDF_PATH = os.getenv("PDF_PATH", str(pathlib.Path(__file__).parent / "document" / "estados_financieros__pdf_93834000_202403.pdf"))
    if not os.path.exists(PDF_PATH):
        logger.error(f"No se encontró el archivo PDF: {PDF_PATH}")
        raise FileNotFoundError(f"No se encontró el archivo PDF: {PDF_PATH}")
    with open(PDF_PATH, "rb") as f:
        pdf_content = f.read()
    return pdf_content

# Solo inicializar vectore_storage si se ejecuta como script principal
if __name__ == "__main__":
    pdf_content = load_pdf_content()
    vectore_storage = search_vectorestore(pdf_content)
    logger.info(f"Almacenamiento de vectores listo")


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


# evaluador de balance total
def evaluate_balance_totals(llm, texto_balance: str):
    """
    Evalua la respuesta obtenida por el primer agente (el que obtiene el balance)
    En la evaluacion verifica si existe los totales o tiene que geerar su suma
    """
    chain = prompt_total_balance | llm | StrOutputParser()
    return chain.invoke({"balance_texto": texto_balance})


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
