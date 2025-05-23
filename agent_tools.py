"""
Herramientas y agentes para extracción de información financiera usando LLM y vector store.
"""
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import ChatPromptTemplate
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Los prompts y el LLM deben ser importados desde el pipeline principal

def make_agent(llm, tool, prompt):
    """
    Crea un agente react para una tarea específica.
    """
    return create_react_agent(llm, tools=[tool], prompt=prompt)

@tool
def extract_company_info(query: str, vectore_storage=None) -> str:
    """
    Tool para extraer información de la empresa desde el vector store usando una consulta.
    """
    if vectore_storage is None:
        logger.error("No se proporcionó vectore_storage")
        return ""
    results = vectore_storage.invoke(query)
    return "\n".join([doc.page_content for doc in results])

@tool
def extract_balance_sheet(query: str, vectore_storage=None) -> str:
    """
    Extrae datos del balance general de la empresa del vectore storage.
    """
    if vectore_storage is None:
        logger.error("No se proporcionó vectore_storage")
        return ""
    results = vectore_storage.invoke(query)
    return "\n".join([doc.page_content for doc in results])

@tool
def extract_income_statement(query: str, vectore_storage=None) -> str:
    """
    Tool para extraer datos del estado de resultados desde el vector store.
    """
    if vectore_storage is None:
        logger.error("No se proporcionó vectore_storage")
        return ""
    results = vectore_storage.invoke(query)
    return "\n".join([doc.page_content for doc in results])
