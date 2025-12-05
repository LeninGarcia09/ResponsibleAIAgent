"""
Shared utility functions and services for the Responsible AI Agent backend.
"""

from .azure_clients import (
    get_cosmos_client,
    get_blob_client,
    get_openai_client,
    get_keyvault_client,
    get_graph_client
)
from .models import (
    AIReviewSubmission,
    ReviewResult,
    ResponsibleAIPrinciple,
    SecurityCheck
)
from .config import Settings

__all__ = [
    'get_cosmos_client',
    'get_blob_client',
    'get_openai_client',
    'get_keyvault_client',
    'get_graph_client',
    'AIReviewSubmission',
    'ReviewResult',
    'ResponsibleAIPrinciple',
    'SecurityCheck',
    'Settings'
]
