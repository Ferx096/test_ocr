import logging
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from e_config import get_embedding
from a_ocr_extractor import concat_text

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def embeddings_guia(guia_data: str):
    """
    Procesa un texto en formato Markdown y lo divide en fragmentos para embeddings.
    Args:
        guia_data (str): Contenido del archivo .md como string.
    Returns:
        List[Document]: Lista de objetos Document con metadatos.
    """
    logger.info("Documento de guía Markdown recibido para dividir")
    # Inicializar el splitter
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=20)
    # Aplicar el split al texto completo
    chunks = text_splitter.split_text(guia_data)
    # Crear documentos con metadatos
    docs = [Document(page_content=chunk, metadata={"fuente": "guia financiera"}) for chunk in chunks]
    logger.info("Split aplicado al documento completo y documentos creados con metadatos")
    return docs

def search_vectorestore(pdf_content, guia_data):
    """
    Transforma el texto concatenado en embedding y lo guarda en un vectorstore, listo para ser invocado
    """
    embedding = get_embedding()
    docs_finance = concat_text(pdf_content)
    docs_guia = embeddings_guia(guia_data)
    # combinar antes de vectorizar
    docs_merge = docs_guia + docs_finance
    logger.info(f"Documentos combinados para vectore store")
    # vectore store - embedding
    vectore_store = FAISS.from_documents(docs_merge, embedding)
    #recuperador
    retriever = vectore_store.as_retriever()
    logger.info(f"Vector Store y recuperación lista")
    return retriever
