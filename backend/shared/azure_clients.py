"""
Azure client initialization and management.
"""
import os
import logging
from typing import Optional
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.cosmos import CosmosClient
from azure.storage.blob import BlobServiceClient
from azure.keyvault.secrets import SecretClient
from openai import AzureOpenAI
import msal
from .config import settings

logger = logging.getLogger(__name__)


def get_azure_credential():
    """Get Azure credential for authentication."""
    # Use ClientSecretCredential if credentials are provided, otherwise DefaultAzureCredential
    if settings.graph_api_client_id and settings.graph_api_client_secret and settings.graph_api_tenant_id:
        return ClientSecretCredential(
            tenant_id=settings.graph_api_tenant_id,
            client_id=settings.graph_api_client_id,
            client_secret=settings.graph_api_client_secret
        )
    return DefaultAzureCredential()


def get_cosmos_client() -> Optional[CosmosClient]:
    """Initialize and return Cosmos DB client."""
    try:
        if not settings.cosmos_db_endpoint or not settings.cosmos_db_key:
            logger.warning("Cosmos DB credentials not configured")
            return None
        
        client = CosmosClient(
            url=settings.cosmos_db_endpoint,
            credential=settings.cosmos_db_key
        )
        logger.info("Cosmos DB client initialized successfully")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize Cosmos DB client: {str(e)}")
        return None


def get_blob_client() -> Optional[BlobServiceClient]:
    """Initialize and return Blob Storage client."""
    try:
        if not settings.storage_connection_string:
            logger.warning("Blob Storage connection string not configured")
            return None
        
        client = BlobServiceClient.from_connection_string(
            settings.storage_connection_string
        )
        logger.info("Blob Storage client initialized successfully")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize Blob Storage client: {str(e)}")
        return None


def get_openai_client() -> Optional[AzureOpenAI]:
    """Initialize and return Azure OpenAI client."""
    try:
        if not settings.azure_openai_endpoint or not settings.azure_openai_api_key:
            logger.warning("Azure OpenAI credentials not configured")
            return None
        
        client = AzureOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version
        )
        logger.info("Azure OpenAI client initialized successfully")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize Azure OpenAI client: {str(e)}")
        return None


def get_keyvault_client() -> Optional[SecretClient]:
    """Initialize and return Key Vault client."""
    try:
        if not settings.azure_key_vault_uri:
            logger.warning("Key Vault URI not configured")
            return None
        
        credential = get_azure_credential()
        client = SecretClient(
            vault_url=settings.azure_key_vault_uri,
            credential=credential
        )
        logger.info("Key Vault client initialized successfully")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize Key Vault client: {str(e)}")
        return None


def get_graph_client():
    """Initialize and return Microsoft Graph API client."""
    try:
        if not all([settings.graph_api_tenant_id, settings.graph_api_client_id, settings.graph_api_client_secret]):
            logger.warning("Microsoft Graph API credentials not configured")
            return None
        
        app = msal.ConfidentialClientApplication(
            settings.graph_api_client_id,
            authority=f"https://login.microsoftonline.com/{settings.graph_api_tenant_id}",
            client_credential=settings.graph_api_client_secret
        )
        
        # Acquire token
        result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
        
        if "access_token" in result:
            logger.info("Microsoft Graph API client initialized successfully")
            return {"client": app, "token": result["access_token"]}
        else:
            logger.error(f"Failed to acquire token: {result.get('error_description')}")
            return None
    except Exception as e:
        logger.error(f"Failed to initialize Microsoft Graph API client: {str(e)}")
        return None
