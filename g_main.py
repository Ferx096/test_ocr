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
# EXPORTAR WORKFLOW COMO MERMAID
# ======================================
def export_stategraph_to_mermaid(graph, path="workflow_graph.mmd"):
    """
    Exporta la estructura del StateGraph a formato Mermaid y la guarda en un archivo.
    """
    nodes = [
        ("company_info", "Company Info"),
        ("balance_sheet", "Balance Sheet"),
        ("final", "Final"),
        ("end", "End")
    ]
    edges = [
        ("company_info", "balance_sheet"),
        ("balance_sheet", "final"),
        ("final", "end")
    ]
    mermaid = ["graph TD"]
    for node, label in nodes:
        mermaid.append(f"    {node}[\"{label}\"]")
    for src, dst in edges:
        mermaid.append(f"    {src} --> {dst}")
    mermaid_code = "\n".join(mermaid)
    with open(path, "w", encoding="utf-8") as f:
        f.write(mermaid_code)
    print(f"Código Mermaid exportado a {path}")

# Ejemplo de uso:
# from e_agents import graph
# export_stategraph_to_mermaid(graph, "workflow_graph.mmd")

# ======================================
# GENERAR PNG DESDE MERMAID (CLI)
# ======================================
def generar_png_mermaid(input_mmd="workflow_graph.mmd", output_png="workflow_graph.png"):
    import subprocess
    try:
        subprocess.run([
            "mmdc", "-i", input_mmd, "-o", output_png
        ], check=True)
        print(f"Imagen PNG generada en {output_png}")
    except Exception as e:
        print(f"Error generando PNG: {e}")

# Ejemplo de uso:
# generar_png_mermaid("workflow_graph.mmd", "workflow_graph.png")

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


