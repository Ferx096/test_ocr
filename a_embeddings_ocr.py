from dotenv import load_dotenv
import os
import pandas as pd
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_core.tools import tool
import json
import re
import logging
from datetime import datetime
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from config import AZURE_CONFIG



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

# cargar datos de guia
url = os.path.join(os.path.dirname(__file__), 'map', 'map_test.json')
with open(url, encoding="utf-8") as f:
    guia_data = json.load(f)
logger.info(f"json de documento guia cargado")


# ======================================
# DOCS GUIE
# ======================================
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.schema import Document


def embeddings_guia(guia_data: str):
    # concatenar terminos del json
    chunks_guie = []
    for cat, content in guia_data.items():
        description = content.get("description", "")  # obtener description
        for termino, definicion in content.get(
            "terminos", {}
        ).items():  # obtener terminos
            texto = f"{cat} - {termino}: {definicion}"
            chunks_guie.append(texto)
    logger.info(f"Documento de guia json listo para ser dividido")

    # chunk-split de la guia de datos
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=20)
    docs = []
    for texto in chunks_guie:
        for chunk in text_splitter.split_text(texto):
            docs.append(
                Document(
                    page_content=chunk,
                    metadata={"fuente": "guia financiera"},
                )
            )
    logger.info("Split aplicado individualmente y documentos creados con metadatos")

    return docs


# ======================================
# OCR+EMBEDINGS / DOCUMENTOS FINACIEROS
# ======================================
"""
El objetivo principal de estas 3 funciones es:
- Extraer texto de un pdf(bytes) con OCR usando Azure, retornando diccioario con el texto extraido
- Convertir el texto y tablas del documento en formato listo para concatenar y poder procesarlo
- Combinar el  documento guia + documento financiero con el objetivo de transformarlos a embeddings
- Una vez creado el embedding, almacenarlo en un solo vector store listo para ser recuperados en consultas
"""


def extract_text_from_pdf_azure(pdf_content: bytes):
    """
    Extrae texto de un PDF usando Azure Document Intelligence
    Args:
        pdf_content (bytes): Contenido del PDF en bytes

    Returns:
        dict: Diccionario con el texto extraído
    """
    logger.info("Analizando PDF con Azure Document Intelligence")

    try:
        # Crear cliente de Document Intelligence
        document_intelligence_client = DocumentIntelligenceClient(
            endpoint=AZURE_CONFIG["endpoint"],
            credential=AzureKeyCredential(AZURE_CONFIG["api_key"]),
        )

        # Analizar el documento
        logger.info("Iniciando análisis del documento...")
        poller = document_intelligence_client.begin_analyze_document(
            "prebuilt-layout", pdf_content
        )

        logger.info("Esperando resultado del análisis...")
        result = poller.result()
        logger.info("Análisis completado correctamente")

        # Extraer texto por página
        text_by_page = []
        for i, page in enumerate(result.pages):
            page_text = ""
            logger.info(f"Página {i + 1}: {len(page.lines)} líneas")
            for line in page.lines:
                page_text += line.content + "\n"
            text_by_page.append(page_text)

        # Extraer tablas
        tables_data = []
        logger.info(
            f"Número de tablas detectadas: {len(result.tables) if result.tables else 0}"
        )
        if result.tables:
            for i, table in enumerate(result.tables):
                table_rows = []
                for cell in table.cells:
                    table_rows.append(
                        {
                            "row_index": cell.row_index,
                            "column_index": cell.column_index,
                            "content": cell.content,
                        }
                    )
                tables_data.append(table_rows)

        full_text = "\n".join(text_by_page)
        logger.info(f"Texto extraído: {len(full_text)} caracteres")

        return {
            "full_text": full_text,
            "text_by_page": text_by_page,
            "tables_data": tables_data,
        }

    except Exception as e:
        logger.error(f"Error al extraer texto del PDF: {e}")
        import traceback

        logger.error(traceback.format_exc())
        return None


# Convertir tablas en markdown
def concat_text(pdf_content):
    """
    Conserva el texto obtenido del diccionario y convierte en markdown las tablas
    Se hace split al texto concatenado, de esta forma podra procesarlas para embedding
    return = split (texto + tabla contetanado)
    """
    result = extract_text_from_pdf_azure(pdf_content)
    # guardar texto
    full_text = result["full_text"]
    logger.info(f"Full texto extraido")
    # tablas a formato string
    import pandas as pd

    tables_text = ""

    for table in result["tables_data"]:
        # Determinar el número máximo de filas y columnas
        max_row = max(cell["row_index"] for cell in table) + 1
        max_col = max(cell["column_index"] for cell in table) + 1
        # Inicializar una matriz vacía
        matrix = [["" for _ in range(max_col)] for _ in range(max_row)]

        # Rellenar la matriz con los valores de la tabla
        for cell in table:
            row, col = cell["row_index"], cell["column_index"]
            matrix[row][col] = cell["content"]

        # Crear el DataFrame
        df = pd.DataFrame(matrix)
        tables_text += df.to_markdown(index=False) + "\n\n"
        logger.info(f"Tablas transformadas a formato markdown")
    """
    
    tables_text = ""
    for table in result["tables_data"]:
        df = (
            pd.DataFrame(
                {
                    (cell["row_index"], cell["column_index"]): cell["content"]
                    for cell in table
                }
            )
            .unstack()
            .fillna("")
        )
        tables_text += df.to_markdown(index=False) + "\n\n"
    logger.info(f"Tablas transformadas a formato markdown")
    """
    # concatenar texto y tablas
    concat_content = full_text + "\n\n" + tables_text
    logger.info(f"Texto de documento de usuario concatenado")

    # split
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=20)
    chunks = text_splitter.split_text(concat_content)
    docs_finance = [Document(page_content=chunk) for chunk in chunks]
    logger.info(f"Split  de documento de usuario listo")

    return docs_finance


# Crear embeddings y guardarlos en un vectore store
def search_vectorestore(pdf_content):
    """
    Transformas el texto concatenado en embedding y lo guarda en un vectorstore, listo para ser invocado
    """
    docs_finance = concat_text(pdf_content)
    docs_guia = embeddings_guia(guia_data)
    # combinar antes de vectorizar
    docs_merge = docs_guia + docs_finance
    logger.info(f"Documentos combinados para vectore store")
    # vectore store -embedding
    vectore_store = FAISS.from_documents(docs_merge, embedding)  # search FAISS
    retrieverr = vectore_store.as_retriever()
    logger.info(f"Vector Store y recuperacion lista")
    return retrieverr
