import logging
from d_agents import extract_company_info
from b_embeddings import search_vectorestore

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def main():
    # Ejemplo de pipeline principal
    with open("document/estados_financieros__pdf_93834000_202403.pdf", "rb") as f:
        pdf_content = f.read()
    with open("map/map_test.md", encoding="utf-8") as f:
        guia_data = f.read()
    vectore_storage = search_vectorestore(pdf_content, guia_data)
    # Ejemplo de consulta
    query = "Extrae la información de la empresa"
    result = extract_company_info(query, vectore_storage)
    print(result)

if __name__ == "__main__":
    main()
