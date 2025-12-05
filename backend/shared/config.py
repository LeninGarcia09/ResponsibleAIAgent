"""
Configuration settings for the Responsible AI Agent backend.
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Azure OpenAI
    azure_openai_endpoint: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    azure_openai_api_key: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    azure_openai_deployment_name: str = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")
    azure_openai_api_version: str = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    
    # Cosmos DB
    cosmos_db_endpoint: str = os.getenv("COSMOS_DB_ENDPOINT", "")
    cosmos_db_key: str = os.getenv("COSMOS_DB_KEY", "")
    cosmos_db_database_name: str = os.getenv("COSMOS_DB_DATABASE_NAME", "ResponsibleAIDB")
    cosmos_db_container_name: str = os.getenv("COSMOS_DB_CONTAINER_NAME", "AIReviews")
    
    # Blob Storage
    storage_connection_string: str = os.getenv("STORAGE_CONNECTION_STRING", "")
    storage_container_reports: str = os.getenv("STORAGE_CONTAINER_REPORTS", "reports")
    
    # Microsoft Graph API
    graph_api_tenant_id: str = os.getenv("GRAPH_API_TENANT_ID", "")
    graph_api_client_id: str = os.getenv("GRAPH_API_CLIENT_ID", "")
    graph_api_client_secret: str = os.getenv("GRAPH_API_CLIENT_SECRET", "")
    
    # Azure Key Vault
    azure_key_vault_uri: str = os.getenv("AZURE_KEY_VAULT_URI", "")
    
    # Email Configuration
    email_from: str = os.getenv("EMAIL_FROM", "noreply@microsoft.com")
    email_subject_prefix: str = os.getenv("EMAIL_SUBJECT_PREFIX", "[Responsible AI Review]")
    
    # Feature Flags
    enable_email_notifications: bool = os.getenv("ENABLE_EMAIL_NOTIFICATIONS", "true").lower() == "true"
    enable_pdf_reports: bool = os.getenv("ENABLE_PDF_REPORTS", "true").lower() == "true"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Singleton settings instance
settings = Settings()
