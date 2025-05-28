import logging
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from e_config import AZURE_CONFIG

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
        result = poller.result()
        text_by_page = []
        for i, page in enumerate(result.pages):
            page_text = ""
            for line in page.lines:
                page_text += line.content + "\n"
            text_by_page.append(page_text)
        tables_data = []
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

def concat_text(pdf_content):
    """
    Convierte el texto y las tablas extraídas en markdown y las concatena.
    """
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.schema import Document
    import pandas as pd
    result = extract_text_from_pdf_azure(pdf_content)
    full_text = result["full_text"]
    tables_text = ""
    for table in result["tables_data"]:
        max_row = max(cell["row_index"] for cell in table) + 1
        max_col = max(cell["column_index"] for cell in table) + 1
        matrix = [["" for _ in range(max_col)] for _ in range(max_row)]
        for cell in table:
            row, col = cell["row_index"], cell["column_index"]
            matrix[row][col] = cell["content"]
        df = pd.DataFrame(matrix)
        tables_text += df.to_markdown(index=False) + "\n\n"
    concat_content = full_text + "\n\n" + tables_text
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=20)
    chunks = text_splitter.split_text(concat_content)
    docs_finance = [Document(page_content=chunk) for chunk in chunks]
    return docs_finance
