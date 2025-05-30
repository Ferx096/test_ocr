import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.storage.blob import BlobServiceClient
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI

def test_azure_document_intelligence():
    endpoint = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
    key = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")
    try:
        client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))
        print("Azure Document Intelligence: OK")
    except Exception as e:
        print("Azure Document Intelligence: ERROR", e)

def test_azure_blob():
    conn_str = os.getenv("AZURE_BLOB_CONNECTION_STRING")
    try:
        blob_service_client = BlobServiceClient.from_connection_string(conn_str)
        containers = list(blob_service_client.list_containers())
        print("Azure Blob Storage: OK, containers:", [c['name'] for c in containers])
    except Exception as e:
        print("Azure Blob Storage: ERROR", e)

def test_azure_openai_embedding():
    try:
        embedding = AzureOpenAIEmbeddings(
            api_version=os.getenv("OPENAI_EMBEDDING_API_VERSION"),
            deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            model="text-embedding-3-large",
        )
        # Intenta una llamada mínima (esto puede requerir un input real)
        print("Azure OpenAI Embedding: OK (instanciado)")
    except Exception as e:
        print("Azure OpenAI Embedding: ERROR", e)

def test_azure_openai_chat():
    try:
        llm = AzureChatOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_version=os.getenv("OPENAI_API_VERSION"),
            deployment_name=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
            model_name="gpt-4",
        )
        print("Azure OpenAI Chat: OK (instanciado)")
    except Exception as e:
        print("Azure OpenAI Chat: ERROR", e)

if __name__ == "__main__":
    test_azure_document_intelligence()
    test_azure_blob()
    test_azure_openai_embedding()
    test_azure_openai_chat()