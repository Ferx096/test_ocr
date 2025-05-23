"""
Utilidades varias para el pipeline financiero.
"""
import json
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

def evaluate_balance_totals(llm, texto_balance, prompt_total_balance_runnable):
    """
    Evalúa si existen totales en el balance, y si no, los calcula sumando los valores de cada bloque.
    Recibe el texto del balance, lo procesa y retorna el resultado evaluado.
    """
    chain = prompt_total_balance_runnable | llm | StrOutputParser()
    if isinstance(texto_balance, dict):
        texto_balance_str = json.dumps(texto_balance, ensure_ascii=False)
    else:
        texto_balance_str = texto_balance
    return chain.invoke({"texto_balance": texto_balance_str})
