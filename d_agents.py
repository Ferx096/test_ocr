from dotenv import load_dotenv
import os
import logging
from langchain_core.messages import HumanMessage
from b_embeddings import search_vectorestore
from datetime import datetime
# from c_tools import State, extract_company_info, agent_company_info, parse_company_info, extract_balance_sheet, parse_number, sum_group, agent_balance_sheet, evaluate_balance_totals, pdf_content
# (Migrar o reimplementar estas funciones en los nuevos módulos según sea necesario)

# ======================================
# CARAGR DATOS
# ======================================
load_dotenv()

# configuracion de logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# llm
from e_config import get_llm

llm = get_llm()
logger.info(f"Azure LLM cargado")

# LANGSMIT
from langsmith import utils

LANGSMITH_ENDPOINT = os.getenv("LANGSMITH_ENDPOINT")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT")
logger.info("LangSmith cargado")
if utils.tracing_is_enabled():
    logger.info("LangSmith tracing está habilitado")
else:
    logger.warning("LangSmith tracing NO está habilitado")
# Traer la estructura del agente
"""Estructura de estado compartido entre agentes"""
# State eliminado para simplificar el pipeline modular

# Cargar contenido
# pdf_content y vectore_storage serán gestionados desde f_main.py en la nueva estructura modular


# ======================================
# NODO DE INFORMACION DE LA COMPAÑIA
# ======================================
# herramienta de info de compañia
"""Extrae informacion de la empresa desde vector store"""
def extract_company_info(query: str, vectore_storage) -> str:
    """
    Extrae información de la empresa desde vector store
    """
    results = vectore_storage.invoke(query)
    return "\n".join([doc.page_content for doc in results])


# NODO COMPANY
