"""Pytest-based smoke tests covering key backend modules."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from shared.config import settings
from shared.models import (
    AIReviewSubmission,
    ResponsibleAIPrinciple,
    SecurityCheckType,
    ReviewStatus,
    Finding,
    SeverityLevel,
)


def test_config_settings_loads() -> None:
    """Ensure mandatory configuration values are available."""

    assert settings.cosmos_db_database_name, "Cosmos DB database name should be configured"
    assert settings.storage_container_reports, "Storage container should be configured"
    assert settings.email_from, "Sender email must be configured"


def test_model_instantiation() -> None:
    """Validate core models can be instantiated with representative data."""

    submission = AIReviewSubmission(
        submitter_email="test@microsoft.com",
        submitter_name="Test User",
        project_name="Test Project",
        project_description="Test Description",
        ai_capabilities=["NLP"],
        data_sources=["Test Data"],
        user_impact="Low",
        deployment_stage="Development",
    )

    assert submission.project_name == "Test Project"
    assert "NLP" in submission.ai_capabilities
    assert submission.deployment_stage.lower() == "development"
    assert len(list(ResponsibleAIPrinciple)) > 0
    assert len(list(SecurityCheckType)) > 0
    assert ReviewStatus.PENDING.value


def test_function_directories_present() -> None:
    """Confirm Azure Function directory scaffolding remains intact."""

    backend_root = Path(__file__).parent
    function_dirs = ["SubmitReview", "ProcessReview", "GenerateReport"]

    missing = []
    for func_dir in function_dirs:
        init_file = backend_root / func_dir / "__init__.py"
        config_file = backend_root / func_dir / "function.json"
        if not (init_file.exists() and config_file.exists()):
            missing.append(func_dir)

    assert not missing, f"Missing Azure Function scaffolding for: {', '.join(missing)}"


def test_finding_model_defaults() -> None:
    """Ensure Finding model captures critical attributes without errors."""

    finding = Finding(
        principle=ResponsibleAIPrinciple.FAIRNESS,
        severity=SeverityLevel.HIGH,
        title="Test Finding",
        description="Test description",
        recommendation="Test recommendation",
        compliant=False,
    )

    assert finding.principle == ResponsibleAIPrinciple.FAIRNESS
    assert finding.severity == SeverityLevel.HIGH
    assert finding.compliant is False


@pytest.mark.parametrize(
    "factory_name",
    [
        "get_cosmos_client",
        "get_blob_client",
        "get_openai_client",
        "get_keyvault_client",
        "get_graph_client",
    ],
)
def test_azure_client_factories_importable(factory_name: str) -> None:
    """Verify Azure client factory functions are defined and callable."""

    from shared import azure_clients

    factory = getattr(azure_clients, factory_name, None)
    assert callable(factory), f"{factory_name} should be a callable factory"
