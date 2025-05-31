import logging
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from f_config import get_embedding
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
    # Dividir en líneas y filtrar solo ítems relevantes
    # Extraer solo los ítems de lista markdown, ignorando encabezados
    docs = []
    for line in guia_data.splitlines():
        l = line.strip()
        if l.startswith('- '):
            docs.append(Document(page_content=l[2:].strip(), metadata={"fuente": "guia financiera"}))
    print(f'[DEBUG] lines: {guia_data.splitlines()}, docs: {[d.page_content for d in docs]}')
    logger.info("Split por ítem aplicado y documentos creados con metadatos")
    print(f'[DEBUG] docs: {[d.page_content for d in docs]}')
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
