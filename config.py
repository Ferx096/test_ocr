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

# Configuración de Azure Document Intelligence
AZURE_CONFIG = {
    "endpoint": os.getenv(
        "AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT",
        "https://asoxdoc.cognitiveservices.azure.com/"
    ),
    "api_key": os.getenv(
        "AZURE_DOCUMENT_INTELLIGENCE_KEY",
        "4fl7ieA4uwJABfXmDcFlviVBPRQ6h5GlZyoSxKxup9St5x1XlIfLJQQJ99BEACYeBjFXJ3w3AAALACOGn9jy",
    ),
    "account_key": os.getenv(
        "ACCOUNT_KEY",
        "A5f2P34SQOM6yDuIw0xu0we1Hj08VLuIrIN2BCPYzA2NL7h5wDC7JQQJ99BEACYeBjFXJ3w3AAALACOGYKtB",
    ),
}

# Configuración de Azure Blob Storage
AZURE_BLOB_CONFIG = {
    "connection_string": os.getenv("AZURE_BLOB_CONNECTION_STRING"),
    "container_name": os.getenv("AZURE_BLOB_CONTAINER_NAME", "pdf"),
    "account_name": os.getenv("AZURE_BLOB_ACCOUNT_NAME", "storagepdf2"),
    "account_key": os.getenv("AZURE_BLOB_ACCOUNT_KEY"),
    "endpoint_suffix": os.getenv("AZURE_BLOB_ENDPOINT_SUFFIX", "core.windows.net"),
}

# Configuración de Azure para autenticación
AZURE_AUTH_CONFIG = {
    "tenant_id": os.getenv("AZURE_TENANT_ID"),
    "subscription_id": os.getenv("AZURE_SUBSCRIPTION_ID"),
    "client_id": os.getenv("AZURE_CLIENT_ID"),
    "client_secret": os.getenv("AZURE_CLIENT_SECRET"),
    "authority_host": os.getenv(
        "AZURE_AUTHORITY_HOST", "https://login.microsoftonline.com"
    ),
    "resource_group": os.getenv("AZURE_RESOURCE_GROUP"),
}


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

# Registrar información de configuración
logger.info(f"Azure Document Intelligence Endpoint: {AZURE_CONFIG['endpoint']}")
logger.info(f"Azure Blob Storage Account: {AZURE_BLOB_CONFIG['account_name']}")
logger.info(f"Azure Tenant ID: {AZURE_AUTH_CONFIG['tenant_id']}")
logger.info(f"Azure Subscription ID: {AZURE_AUTH_CONFIG['subscription_id']}")
