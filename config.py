"""
Configuración para el servicio OCR.
"""

import os
import logging
from dotenv import load_dotenv

# Configurar logging
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

# Configuración centralizada de Azure
AZURE_CONFIG = {
    "endpoint": os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT"),
    "api_key": os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY"),
}

AZURE_BLOB_CONFIG = {
    "connection_string": os.getenv("AZURE_BLOB_CONNECTION_STRING"),
    "container_name": os.getenv("AZURE_BLOB_CONTAINER_NAME", "pdf"),
    "account_name": os.getenv("AZURE_BLOB_ACCOUNT_NAME", "storagepdf2"),
    "account_key": os.getenv("AZURE_BLOB_ACCOUNT_KEY"),
    "endpoint_suffix": os.getenv("AZURE_BLOB_ENDPOINT_SUFFIX", "core.windows.net"),
}
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings

def get_llm():
    return AzureChatOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_version=os.getenv("OPENAI_API_VERSION"),
        deployment_name=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
        model_name="gpt-4",
    )

def get_embedding():
    return AzureOpenAIEmbeddings(
        api_version=os.getenv("OPENAI_EMBEDDING_API_VERSION"),
        deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        model="text-embedding-3-large",
    )




# Asegurarse de que AZURE_BLOB_CONFIG esté definido globalmente
if not AZURE_BLOB_CONFIG["connection_string"]:
    # Construir connection string manualmente si no está definido
    account_name = AZURE_BLOB_CONFIG["account_name"]
    account_key = AZURE_BLOB_CONFIG["account_key"]
    endpoint_suffix = AZURE_BLOB_CONFIG["endpoint_suffix"]
    if account_name and account_key:
        AZURE_BLOB_CONFIG["connection_string"] = (
            f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix={endpoint_suffix}"
        )
        logger.info("Connection string construido manualmente")
    else:
        logger.warning(
            "No se pudo construir connection_string, faltan account_name o account_key"
        )

# Definir AZURE_AUTH_CONFIG antes de usarlo
AZURE_AUTH_CONFIG = {
    'tenant_id': os.getenv('AZURE_TENANT_ID', ''),
    'subscription_id': os.getenv('AZURE_SUBSCRIPTION_ID', '')
}
# Registrar información de configuración
logger.info(f"Azure Document Intelligence Endpoint: {AZURE_CONFIG['endpoint']}")
logger.info(f"Azure Blob Storage Account: {AZURE_BLOB_CONFIG['account_name']}")
logger.info(f"Azure Tenant ID: {AZURE_AUTH_CONFIG['tenant_id']}")
logger.info(f"Azure Subscription ID: {AZURE_AUTH_CONFIG['subscription_id']}")
