import logging
from b_embeddings import search_vectorestore


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ======================================
# GRAPH VISUALIZATION
# ======================================
"""
from langchain_core.runnables.graph_mermaid import MermaidDrawMethod
from IPython.display import Image, display

# generar imagen
imagen = app.get_graph().draw_mermaid_png()
# guardar imagen
with open(path_graph, "wb") as f:
    f.write(imagen)
print("imagen del workflow guardada")
logger.info(f"imagen del workflow guardada")
"""
# ======================================
#CREAR EL VECTOR STORE PARA LA BUSQUEDA
# ======================================
import sys
if 'pytest' not in sys.modules:
    #importar documento base-guia
    with open("map/map_test.md", "r", encoding="utf-8") as f_guia:
        guia_data = f_guia.read()
    #importar documento para prueba
    with open("document/estados_financieros__pdf_93834000_202403.pdf", "rb") as f:
        pdf_content = f.read()
    #Guardar en el almacen de vectores para una busqueda optima
    vectore_storage = search_vectorestore(pdf_content, guia_data)
else:
    vectore_storage = None


