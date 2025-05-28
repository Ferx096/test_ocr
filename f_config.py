import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings

load_dotenv()

AZURE_CONFIG = {
    "endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
    "api_key": os.getenv("AZURE_OPENAI_API_KEY"),
    "deployment_name": os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
    "embedding_deployment": os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME"),
    "api_version": os.getenv("AZURE_OPENAI_API_VERSION", "2023-05-15"),
}

def get_llm():
    return AzureChatOpenAI(
        azure_endpoint=AZURE_CONFIG["endpoint"],
        api_key=AZURE_CONFIG["api_key"],
        azure_deployment=AZURE_CONFIG["deployment_name"],
        api_version=AZURE_CONFIG["api_version"],
        temperature=0.0,
    )

def get_embedding():
    print(f"[DEBUG] Embedding deployment: {AZURE_CONFIG['embedding_deployment']}")
    return AzureOpenAIEmbeddings(
        azure_endpoint=AZURE_CONFIG["endpoint"],
        api_key=AZURE_CONFIG["api_key"],
        azure_deployment=AZURE_CONFIG["embedding_deployment"],
        api_version=AZURE_CONFIG["api_version"],
    )
