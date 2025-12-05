"""
Simple RAI Agent Evaluation Script

This script tests the RAI Agent responses without requiring the full Azure AI Evaluation SDK.
It calls the deployed backend API and validates responses against expected criteria.
"""

import os
import json
import requests
from datetime import datetime

# Backend API endpoint
API_URL = os.environ.get("RAI_API_URL", "https://rai-backend.graymoss-a8a3aef8.westus3.azurecontainerapps.io/api")


def load_test_cases(test_file: str = "test_cases.json") -> list:
    """Load test cases from JSON file."""
    test_path = os.path.join(os.path.dirname(__file__), test_file)
    with open(test_path, 'r') as f:
        return json.load(f)


def call_rai_api(project_name: str, description: str, review_level: str = "standard") -> dict:
    """Call the deployed RAI Agent API."""
    try:
        response = requests.post(
            f"{API_URL}/submit-review",
            json={
                "projectName": project_name,
                "description": description,
                "reviewLevel": review_level
            },
            timeout=120
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def validate_response(response: dict, expected_aspects: list, review_level: str) -> dict:
    """Validate the agent response against expected criteria."""
    
    validation = {
        "has_error": "error" in response,
        "has_risk_level": "risk_level" in response,
        "has_summary": "summary" in response,
        "has_recommendations": "key_recommendations" in response and len(response.get("key_recommendations", [])) > 0,
        "has_concerns": "concerns" in response,
        "aspects_covered": [],
        "missing_aspects": [],
    }
    
    # Check if response covers expected aspects
    response_text = json.dumps(response).lower()
    for aspect in expected_aspects:
        if aspect.lower() in response_text or aspect.replace("_", " ").lower() in response_text:
            validation["aspects_covered"].append(aspect)
        else:
            validation["missing_aspects"].append(aspect)
    
    # Check for quick-start guide in basic reviews
    if review_level == "basic":
        validation["has_quick_start"] = "quick_start_guide" in response
    
    # Calculate score
    checks = [
        not validation["has_error"],
        validation["has_risk_level"],
        validation["has_summary"],
        validation["has_recommendations"],
        len(validation["aspects_covered"]) > len(validation["missing_aspects"])
    ]
    validation["score"] = sum(checks) / len(checks) * 100
    validation["passed"] = validation["score"] >= 60
    
    return validation


def run_simple_evaluation():
    """Run simple evaluation against the deployed API."""
    
    print("="*60)
    print("🤖 RAI Agent Simple Evaluation")
    print("="*60)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔗 API: {API_URL}")
    
    # Check API health
    print("\n🏥 Checking API health...")
    try:
        health = requests.get(f"{API_URL}/health", timeout=60)
        if health.status_code == 200:
            print("   ✅ API is healthy")
        else:
            print(f"   ⚠️ API returned status {health.status_code}")
    except Exception as e:
        print(f"   ❌ API health check failed: {e}")
        return
    
    # Load test cases
    print("\n📂 Loading test cases...")
    test_cases = load_test_cases()
    print(f"   Found {len(test_cases)} test cases")
    
    results = []
    passed = 0
    failed = 0
    
    print("\n🚀 Running evaluations...")
    print("-"*60)
    
    for case in test_cases:
        print(f"\n📋 Test: {case['name']}")
        print(f"   Level: {case['review_level']}")
        
        # Call API
        response = call_rai_api(
            case['name'],
            case['description'],
            case['review_level']
        )
        
        # Validate response
        validation = validate_response(
            response,
            case['expected_aspects'],
            case['review_level']
        )
        
        # Record result
        result = {
            "id": case["id"],
            "name": case["name"],
            "review_level": case["review_level"],
            "validation": validation,
            "response_preview": str(response)[:200] + "..." if len(str(response)) > 200 else str(response)
        }
        results.append(result)
        
        # Print status
        if validation["passed"]:
            passed += 1
            print(f"   ✅ PASSED (Score: {validation['score']:.0f}%)")
        else:
            failed += 1
            print(f"   ❌ FAILED (Score: {validation['score']:.0f}%)")
        
        if validation["has_error"]:
            print(f"   ⚠️ Error in response")
        
        if validation["missing_aspects"]:
            print(f"   📌 Missing aspects: {', '.join(validation['missing_aspects'])}")
    
    # Summary
    print("\n" + "="*60)
    print("📊 EVALUATION SUMMARY")
    print("="*60)
    print(f"   Total Tests: {len(test_cases)}")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📈 Pass Rate: {passed/len(test_cases)*100:.1f}%")
    
    # Save results
    report = {
        "timestamp": datetime.now().isoformat(),
        "api_url": API_URL,
        "summary": {
            "total": len(test_cases),
            "passed": passed,
            "failed": failed,
            "pass_rate": passed/len(test_cases)*100
        },
        "results": results
    }
    
    report_path = os.path.join(os.path.dirname(__file__), "simple_evaluation_report.json")
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Report saved to: {report_path}")
    print("\n" + "="*60)
    print("✅ Evaluation Complete!")
    print("="*60)
    
    return report


if __name__ == "__main__":
    run_simple_evaluation()
