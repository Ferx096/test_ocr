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
    Si detecta estructura jerárquica (###### nombre), usa el parser avanzado.
    Args:
        guia_data (str): Contenido del archivo .md como string.
    Returns:
        List[Document]: Lista de objetos Document con metadatos.
    """
    if guia_data.strip().startswith('#') or '###### nombre' in guia_data:
        return parse_markdown_guia(guia_data)
    logger.info("Documento de guía Markdown recibido para dividir")
    # Inicializar el splitter
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=20)
    # Dividir en líneas y filtrar solo ítems relevantes
    docs = []
    for line in guia_data.splitlines():
        l = line.strip()
        if l.startswith('- '):
            docs.append(Document(page_content=l[2:].strip(), metadata={"fuente": "guia financiera"}))
    logger.info("Split por ítem aplicado y documentos creados con metadatos")
    return docs



def parse_markdown_guia(md_text):
    """
    Parsea un archivo .md estructurado como map/map_test.md y extrae términos con metadatos.
    Devuelve una lista de Document(page_content=nombre, metadata={...})
    """
    import re
    from langchain.schema import Document
    docs = []
    current = {}
    field = None
    for line in md_text.splitlines():
        l = line.strip()
        # Detectar campos
        m = re.match(r'^(#+) +([a-zA-Z_]+)$', l)
        if m:
            level, campo = len(m.group(1)), m.group(2).lower()
            if level == 6 and campo == 'nombre':
                # Si ya hay un término, guardar
                if 'nombre' in current:
                    # Si el campo es lista, concatenar con punto y coma para page_content
                    page_content = current['nombre']
                    if isinstance(page_content, list):
                        page_content = '; '.join(page_content)
                    docs.append(Document(page_content=page_content, metadata={k: v for k, v in current.items() if k != 'nombre'}))
                    current = {}
                field = 'nombre'
            else:
                field = campo
            continue
        # Acumular valores de campo
        if field and l.startswith('- '):
            val = l[2:].strip()
            if field in current:
                if isinstance(current[field], list):
                    current[field].append(val)
                else:
                    current[field] = [current[field], val]
            else:
                current[field] = val
    # Guardar el último término
    if 'nombre' in current:
        # Si el campo es lista, concatenar con punto y coma para page_content
        page_content = current['nombre']
        if isinstance(page_content, list):
            page_content = '; '.join(page_content)
        docs.append(Document(page_content=page_content, metadata={k: v for k, v in current.items() if k != 'nombre'}))
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
