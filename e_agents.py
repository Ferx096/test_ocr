from dotenv import load_dotenv
import os
import logging
from langchain_core.messages import HumanMessage
from langgraph.types import Command
from typing import Literal
from langgraph.graph import StateGraph, END, MessagesState
from datetime import datetime
from langsmith import utils
from b_embeddings import search_vectorestore
from f_config import get_llm
from d_tools import State
from d_tools import extract_company_info, parse_company_info, extract_balance_sheet, parse_number, sum_group, evaluate_balance_totals, extract_income_statement, agent_income_statement, agent_balance_sheet, agent_company_info

#from g_main import vectore_storage
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
llm = get_llm()
logger.info(f"Azure LLM cargado")

# LANGSMIT
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
State = State



# ======================================
# NODO DE INFORMACION DE LA COMPAÑIA
# ======================================
# herramienta de info de compañia
"""Extrae informacion de la empresa desde vector store"""
extract_company_info = extract_company_info

# agente de info de compañia
agent_company_info = agent_company_info

# parser de info de compañia
"""Extrae informacion del valor del texto corrigiendo  valores innecesarios"""
parse_company_info = parse_company_info

extract_income_statement = extract_income_statement


# NODO COMPANY
def node_company_info(State: State) -> Command[Literal["balance_sheet"]]:
    """
    Nodo que tiene funcion de buscar nombre y rut de la empresa y la fecha del informe
    """
    # obtener query del estado
    query = "Extrae el nombre, RUT y fecha de reporte de la empresa."
    # ejecutar el agente
    response = agent_company_info.invoke({"content": query})
    logger.info(f"Agente de recuperacion de informacion de compañia ejecutado")

    # Extraer el contenido de la respuesta de forma robusta
    if isinstance(response, list):
        if response and isinstance(response[0], dict) and 'content' in response[0]:
            content_str = response[0]['content']
        else:
            content_str = str(response)
    elif hasattr(response, 'content'):
        content_str = response.content
    else:
        content_str = str(response)


    # Validar y parsear la respuesta JSON
    try:
        estructura_company = json.loads(content_str)
        logger.info("Respuesta del agente parseada como JSON correctamente")
    except Exception as e:
        logger.error(f"Error al parsear la respuesta del agente como JSON: {e}. Respuesta: {content_str}")
        # Devolver un dict vacío para evitar fallos posteriores
        estructura_company = {"company_name": None, "company_rut": None, "report_date": None}


    # Aplicar parse_number a cada valor dentro de cada bloque
    def clean(val):
        if isinstance(val, dict):
            return {k: parse_company_info(v) for k, v in val.items()}
        elif isinstance(val, str):
            return parse_company_info(val)
        return None

    company_name = clean(estructura_company.get("company_name", {}))
    company_rut = clean(estructura_company.get("company_rut", {}))
    report_date = clean(estructura_company.get("report_date", {}))
    creacion_report = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"Datos parseados")

    goto = "balance_sheet"

    # actualizar el estado
    logger.info(
        f"Nodo recuperador de informacion de compañia  y actualizacion en proceso"
    )

    return Command(
        goto=goto,
        update={
            # se usa solo content ya que es la respuesta del agente
            "messages": [str(content_str)],
            # aqui se usa el diccionario result
            "nombre_compañia": company_name,
            "rut_compañia": company_rut,
            "fecha_reporte": report_date,
            "creacion_report": creacion_report,
            "next": goto,
        },
    )


# ======================================
# NODO  BALANCE GENERAL
# ======================================

# Herramienta de balance general
"""
Extrae datos del balance general de la empresa del vectore storage.
Dividiendo la inforamcion extraida en activos, pasivos y patrimonio
"""
extract_balance_sheet = extract_balance_sheet

# parser balance general
"""Convierte strings como mil y millon a float. Retorna None si no puede convertir."""
parse_number = parse_number

# sumar valores en caso no exsita suma
"""Suma los valores numéricos de un grupo de cuentas."""
sum_group = sum_group

# agente de balance general
agent_balance_sheet = agent_balance_sheet

# funcion evaluador de los totales de cada balance
"""
Evalua la respuesta obtenida por el primer agente (el que obtiene el balance)
En la evaluacion verifica si existe los totales o tiene que geerar su suma
"""
evaluate_balance_totals = evaluate_balance_totals


# NODO DE BALANCE GENERAL
def node_balance_sheet(state: State) -> Command[Literal["final"]]:
    """
    Nodo que tiene como objetivo obtener todos los datos del balance geneeral
    Trata de calcular  cada dato importante dividiendo en 3 bloques: activos, pasivos y patrimonio
    Marca un enfasis en calcular los totales de bloque en caso no este  lo calcula
    """
    # obtener query del estado
    query = f"Extrae los datos del balance general; activos, pasivos y patrimonio de la empresa {state['nombre_compañia']}. Dame tu respeusta en formato json"
    # ejecutar el agente
    response = agent_balance_sheet.invoke({"content": query})
    logger.info("Agente balance general")

    # Extraer el contenido de la respuesta de forma robusta
    if isinstance(response, dict) and 'messages' in response and response['messages']:
        # Buscar el último mensaje tipo AIMessage con content no vacío
        for msg in reversed(response['messages']):
            if hasattr(msg, 'content') and msg.content:
                texto = msg.content
                break
        else:
            texto = str(response)
    else:
        texto = str(response)
    logger.info(f"Texto recuperado por agente principal.")

    # Usar LLM para evaluar inteligentemente el contenido
    resultado_llm = evaluate_balance_totals(llm, texto)
    logger.info(
        f"Evaluación de totales en el texto principal realizada: {resultado_llm}"
    )

    # Parsear la rpta JSON conviertiendolo en un diccionario
    try:
        estructura_balance = json.loads(resultado_llm.content)
        logger.info(f"Json convertido a diccionario")
    except Exception as e:
        logger.error(f"Error al parsear la respuesta del balance como JSON: {e}. Respuesta: {resultado_llm.content}")
        estructura_balance = {"activos": {}, "pasivos": {}, "patrimonio": {}}

    # Aplicar parse_number a cada valor dentro de cada bloque
    def clean_dict(d):
        return {e: parse_number(v) for e, v in d.items()}

    # parsear la respuesta
    activos = clean_dict(estructura_balance.get("activos", {}))
    pasivos = clean_dict(estructura_balance.get("pasivos", {}))
    patrimonio = clean_dict(estructura_balance.get("patrimonio", {}))
    logger.info("Bloques parseados correctamente.")

    # Trabajar los totales
    total_activos = (
        activos.get("total_activos")
        if "total_activos" in activos
        else sum_group(activos)
    )
    total_pasivos = (
        pasivos.get("total_pasivos")
        if "total_pasivos" in pasivos
        else sum_group(pasivos)
    )
    total_patrimonio = (
        patrimonio.get("total_patrimonio")
        if "total_patrimonio" in patrimonio
        else sum_group(patrimonio)
    )

    # Agregar/actualizar los totales en los diccionarios
    activos["total_activos"] = total_activos
    pasivos["total_pasivos"] = total_pasivos
    patrimonio["total_patrimonio"] = total_patrimonio
    logger.info("Totales calculados y actualizados en los bloques.")

    goto = "final"

    logger.info(f"Nodo recuperador de balance general  y actualizacion en proceso")
    return Command(
        goto=goto,
        update={
            # se usa solo content ya que es la respuesta del agente
            #"messages": {"balance_sheet": response.content}
            "messages": [str(content_str)],
            # aqui se usa el diccionario result
            "balance_general": [activos, pasivos, patrimonio],
            "next": goto,
        },
    )


# ======================================
# NODO  SALIDA
# ======================================
import pandas as pd


def node_final(state: State) -> Command[Literal["end"]]:
    """
    Nodo supervisor que genera una salida y un archivo Excel limpio con los datos de la empresa y su balance general.
    """
    # Extraer datos del estado
    nombre_compañia = state.get("nombre_compañia")
    rut_compañia = state.get("rut_compañia")
    fecha_reporte = state.get("fecha_reporte")
    creacion_report = state.get("creacion_report")
    balance_general = state.get("balance_general")  # activos, pasivos, patrimonio

    # Crear DF para los datos de la empresa
    empresa_info = pd.DataFrame(
        {
            "campo": [
                "Nombre de la empresa",
                "RUT",
                "Fecha del Reporte",
                "Fecha de creacio del reporte",
            ],
            "valor": [nombre_compañia, rut_compañia, fecha_reporte, creacion_report],
        }
    )
    logger.info("Convertir datos de informacion de la empresa a df")

    # DF para el balance general
    activos_df = pd.DataFrame(balance_general[0].items(), columns=["Cuenta", "Activos"])
    pasivos_df = pd.DataFrame(balance_general[1].items(), columns=["Cuenta", "Pasivos"])
    patrimonio_df = pd.DataFrame(
        balance_general[2].items(), columns=["Cuenta", "Patrimonio"]
    )
    logger.info("Convertir datos del balance general a df")
    # Unir los 3 bloques horizontalmente (alineados por fila)
    df_balance_concat = pd.concat([activos_df, pasivos_df, patrimonio_df], axis=1)
    logger.info("Dataframe concatenados")

    # Guardar todo en una sola hoja excel
    name_filed = f"Balance_empresa_{nombre_compañia}.xlsx"
    with pd.ExcelWriter(name_filed, engine="openpyxl") as writer:
        empresa_info.to_excel(writer, index=False, sheet_name="Balance", startrow=0)
        df_balance_concat.to_excel(
            writer, index=False, sheet_name="Balance", startrow=6
        )  # Empieza después de los datos de empresa
    logger.info(f"Archivo Excel generado exitosamente: {name_filed}")

    # Leer el archivo como bytes
    with open(name_filed, "rb") as f:
        excel_bytes = f.read()

    return Command(
        goto="end",
        update={
            "messages": [
                HumanMessage(content="Excel generado correctamente", name="final")
            ],
            "excel_bytes": excel_bytes,  #bytes
        },
    )


def node_end(state: State) -> None:
    # Nodo final, no hace nada o solo marca fin
    print("Proceso finalizado")
    return None


# ======================================
# NODOS Y GRAFOS
# ======================================
graph = StateGraph(State)
graph.add_node("company_info", node_company_info)
graph.add_node("balance_sheet", node_balance_sheet)
graph.add_node("final", node_final)
graph.add_node("end", node_end)
graph.set_entry_point("company_info")
graph.add_edge("company_info", "balance_sheet")
graph.add_edge("balance_sheet", "final")  # <-- Conexión
graph.add_edge("final", "end")  # FIN

app = graph.compile()






