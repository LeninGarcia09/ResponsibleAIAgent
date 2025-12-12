"""
Manual smoke-check script for backend modules without requiring Azure runtime.
Run this file directly when you want quick console validation outside automated tests.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

print("=" * 60)
print("Testing Responsible AI Agent Backend Components")
print("=" * 60)

# Test 1: Config
print("\n[1/5] Testing Configuration...")
try:
    from shared.config import settings
    print("\u2713 Config module loaded")
    print(f"  - Cosmos DB Database: {settings.cosmos_db_database_name}")
    print(f"  - Storage Container: {settings.storage_container_reports}")
    print(f"  - Email From: {settings.email_from}")
except Exception as e:
    print(f"\u2717 Config test failed: {e}")
    sys.exit(1)

# Test 2: Models
print("\n[2/5] Testing Data Models...")
try:
    from shared.models import (
        AIReviewSubmission,
        ReviewResult,
        ResponsibleAIPrinciple,
        SecurityCheckType,
        ReviewStatus,
        Finding,
        SecurityCheck,
        SeverityLevel
    )
    print("\u2713 All models imported successfully")
    print(f"  - Responsible AI Principles: {len(list(ResponsibleAIPrinciple))}")
    print(f"  - Security Check Types: {len(list(SecurityCheckType))}")

    # Test model creation
    submission = AIReviewSubmission(
        submitter_email="test@microsoft.com",
        submitter_name="Test User",
        project_name="Test Project",
        project_description="Test Description",
        ai_capabilities=["NLP"],
        data_sources=["Test Data"],
        user_impact="Low",
        deployment_stage="Development"
    )
    print(f"\u2713 Created test submission: {submission.project_name}")

except Exception as e:
    print(f"\u2717 Models test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Azure Clients (without actual connections)
print("\n[3/5] Testing Azure Client Modules...")
try:
    from shared.azure_clients import (
        get_cosmos_client,
        get_blob_client,
        get_openai_client,
        get_keyvault_client,
        get_graph_client
    )
    print("\u2713 Azure client functions imported")
    print("  - Note: Actual connections require Azure credentials")
except Exception as e:
    print(f"\u2717 Azure clients test failed: {e}")
    sys.exit(1)

# Test 4: Function Modules
print("\n[4/5] Testing Function Modules...")
try:
    # Test if function files exist
    function_dirs = ['SubmitReview', 'ProcessReview', 'GenerateReport']
    for func_dir in function_dirs:
        init_file = os.path.join(func_dir, '__init__.py')
        json_file = os.path.join(func_dir, 'function.json')
        if os.path.exists(init_file) and os.path.exists(json_file):
            print(f"\u2713 {func_dir} function files present")
        else:
            print(f"\u2717 {func_dir} function files missing")
except Exception as e:
    print(f"\u2717 Function modules test failed: {e}")

# Test 5: Review Engine Logic
print("\n[5/5] Testing Review Engine Components...")
try:
    from datetime import datetime
    from shared.models import Finding, SeverityLevel, ResponsibleAIPrinciple

    finding = Finding(
        principle=ResponsibleAIPrinciple.FAIRNESS,
        severity=SeverityLevel.HIGH,
        title="Test Finding",
        description="Test description",
        recommendation="Test recommendation",
        compliant=False
    )
    print(f"\u2713 Created sample finding: {finding.title}")
    print(f"  - Principle: {finding.principle}")
    print(f"  - Severity: {finding.severity}")
    print(f"  - Compliant: {finding.compliant}")

except Exception as e:
    print(f"\u2717 Review engine test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Backend Component Tests Complete!")
print("=" * 60)
print("\nNext Steps:")
print("1. Install Azure Functions Core Tools:")
print("   npm install -g azure-functions-core-tools@4")
print("2. Configure Azure credentials in local.settings.json")
print("3. Run: func start (to start Azure Functions locally)")
print("\nNote: Without Azure credentials, the functions will run but")
print("      won't be able to connect to Azure services.")
