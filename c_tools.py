"""
Herramientas y agentes para extracción y procesamiento de información financiera.
Define agentes jerárquicos, funciones de parsing y utilidades para manipular datos extraídos de documentos.
"""
# Este archivo ha sido refactorizado. Las funciones de parsing están en parsing_tools.py, los agentes en agent_tools.py y las utilidades en utils_tools.py.
# Mantener este archivo solo para compatibilidad temporal o migrar todo el código a los nuevos módulos.

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
    """
    Estructura de estado compartido entre agentes, contiene los campos principales del flujo.
    Incluye mensajes, datos de la compañía, balance general y el siguiente paso del flujo.
    """

    messages: Optional[Annotated[list[HumanMessage], add_messages]]
    nombre_compañia: Optional[str]
    rut_compañia: Optional[str]
    fecha_reporte: Optional[str]
    creacion_report: Optional[dict]
    balance_general: Optional[dict]
    next: Optional[str]


def pdf_content():
    """
    Lee el PDF de entrada y retorna su contenido en bytes para procesamiento.
    """
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


@tool
def extract_company_info(query: str) -> str:
    """
    Tool para extraer información de la empresa desde el vector store usando una consulta.
    """
    """
    Extrae informacion de la empresa desde vector store
    """
    results = vectore_storage.invoke(query)
    return "\n".join([doc.page_content for doc in results])


# agente

def parse_company_info(response_text: str) -> dict:
    """
    Extrae y limpia los campos de nombre, RUT y fecha desde el texto de respuesta del agente.
    """
    # ... (lógica de extracción)

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
    """
    Tool para extraer datos del balance general desde el vector store, dividiendo en bloques.
    """
            else None
        ),
        "report_date": date_match.group(1).strip() if date_match else None,
    }

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
    Convierte strings como "mil" y "millón" a float, o retorna None si no es posible.
    Intenta extraer el valor numérico de un string, considerando palabras como 'mil' y 'millón'.
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
    """
    Evalúa si existen totales en el balance, y si no, los calcula sumando los valores de cada bloque.
    """
            return number
    except Exception:
        return None


# Sumar valores en caso no exista suma:
def sum_group(grupo: Dict[str, str]) -> float:
    """
    Suma los valores numéricos de un grupo de cuentas (dict).
    """
    return sum(parse_number(e) for e in grupo.values())


# agente
agent_balance_sheet = create_react_agent(
    llm, tools=[extract_balance_sheet], prompt=prompt_balance_sheet
)
prompt_total_balance_runnable = ChatPromptTemplate.from_template(prompt_total_balance)

    """
    Tool para extraer datos del estado de resultados desde el vector store.
    """


# evaluador de balance total
def evaluate_balance_totals(llm, texto_balance: str):
    """
    Evalúa si existen totales en el balance, y si no, los calcula sumando los valores de cada bloque.
    Recibe el texto del balance, lo procesa y retorna el resultado evaluado.
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
    Tool para extraer datos del estado de resultados desde el vector store.
    Extrae datos de estado de resultados de la empresa del vectore storage, dividiendo la información extraída en bloques.
    """
    results = vectore_storage.invoke(query)
    return "\n".join([doc.page_content for doc in results])


# Se usara el mismo parse_number pde balance general

# agente de balance de resultados
agent_income_statement = create_react_agent(
    llm, tools=[extract_income_statement], prompt=prompt_income_statement
)
