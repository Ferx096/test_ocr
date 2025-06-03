import logging
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from f_config import AZURE_CONFIG
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import pandas as pd

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

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
        document_intelligence_client = DocumentIntelligenceClient(
            endpoint=AZURE_CONFIG["endpoint"],
            credential=AzureKeyCredential(AZURE_CONFIG["api_key"]),
        )
        poller = document_intelligence_client.begin_analyze_document(
            "prebuilt-layout", pdf_content
        )
        logger.info("Esperando resultado del análisis...")
        result = poller.result()
        logger.info("Análisis completado correctamente")

        ## Extraer texto por página
        text_by_page = []
        for i, page in enumerate(result.pages):
            page_text = ""
            logger.info(f"Página {i + 1}: {len(page.lines)} líneas")
            for line in page.lines:
                page_text += line.content + "\n"
            text_by_page.append(page_text)

        # Extraer tablas
        tables_data = []
        logger.info(f"Número de tablas detectadas: {len(result.tables) if result.tables else 0}")

        if result.tables:
            for table in result.tables:
                table_rows = []
                for cell in table.cells:
                    table_rows.append({
                        "row_index": cell.row_index,
                        "column_index": cell.column_index,
                        "content": cell.content,
                    })
                tables_data.append(table_rows)
        full_text = "\n".join(text_by_page)
        logger.info(f"Texto extraído: {len(full_text)} caracteres")

        return {
    """
    Convierte el resultado OCR (texto y tablas) en un único string concatenado y lo divide en chunks para embeddings.
    """
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
    Convierte el texto y las tablas extraídas en markdown y las concatena.
    Conserva el texto obtenido del diccionario y convierte en markdown las tablas
    Se hace split al texto concatenado, de esta forma podra procesarlas para embedding
    return = split (texto + tabla contetanado)
    """
    result = extract_text_from_pdf_azure(pdf_content)
    if not result or "full_text" not in result:
        logger.error("No se pudo extraer texto del PDF. El resultado es None o no contiene 'full_text'.")
        return None

    # guardar texto
    full_text = result["full_text"]
    logger.info(f"Full texto extraido")

    # tablas a formato string
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

        #crear el df
        df = pd.DataFrame(matrix)
        tables_text += df.to_markdown(index=False) + "\n\n"
        logger.info(f"Tablas transformadas a formato markdown")

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
    # Fin bloque comentado

    # concatenar texto y tablas
    concat_content = full_text + "\n\n" + tables_text
    logger.info(f"Texto de documento de usuario concatenado")

    # split
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=20)
    chunks = text_splitter.split_text(concat_content)
    docs_finance = [Document(page_content=chunk) for chunk in chunks]
    logger.info(f"Split  de documento de usuario listo")
    return docs_finance
