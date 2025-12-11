"""
Lightweight MCP-style stdio server exposing curated tools/resources for grounding.

Protocol (minimal JSON-RPC-ish over newline-delimited JSON):
  - {"id": "...", "method": "list_tools"}
  - {"id": "...", "method": "call_tool", "params": {"name": "risk_score", "args": {...}}}
  - {"id": "...", "method": "list_resources"}

This is intentionally small and dependency-free; it is not a full MCP reference
implementation but provides a compatible surface for agents that can invoke
tools/resources via stdio/JSON.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List


############################
# Tool implementations
############################


def calculate_basic_risk_scores(project_data: Dict[str, Any]) -> Dict[str, Any]:
    """Deterministic fallback risk score to ground UI and agent responses."""

    overall = 55
    drivers_pos: List[str] = []
    drivers_neg: List[str] = []

    stage = (project_data.get("deployment_stage") or "").lower()
    description = (project_data.get("project_description") or "").lower()
    capabilities = project_data.get("ai_capabilities") or []

    def bump(amount: int, reason: str, positive: bool = False) -> None:
        nonlocal overall
        overall += amount
        (drivers_pos if positive else drivers_neg).append(reason)

    if stage in ["production", "ga", "live"]:
        bump(10, "Production deployment increases risk")
    if any(word in description for word in ["health", "medical", "patient"]):
        bump(12, "Health-related use case")
    if any(word in description for word in ["financial", "bank", "payment", "loan"]):
        bump(10, "Financial decisioning or data")
    if any(word in description for word in ["children", "minor", "student"]):
        bump(8, "Impacts children or minors")
    if any(word in description for word in ["biometric", "facial", "face", "voiceprint"]):
        bump(10, "Biometric data involved")

    high_risk_caps = {"personal_data", "decisions", "facial_recognition", "health_data", "financial"}
    if any(cap in high_risk_caps for cap in capabilities):
        bump(12, "High-risk AI capability selected")

    overall = max(0, min(95, overall))

    if overall >= 85:
        level = "High"
    elif overall >= 70:
        level = "Medium"
    else:
        level = "Low"

    principle_base = max(50, min(90, overall))
    principle_scores = {
        "reliability_safety": principle_base,
        "privacy_security": min(95, principle_base + 5 if drivers_neg else principle_base),
        "fairness": principle_base,
        "transparency": principle_base - 2,
        "inclusiveness": principle_base - 3,
        "accountability": principle_base - 1,
    }

    return {
        "overall_score": overall,
        "risk_level": level,
        "risk_summary": "Preliminary risk estimate based on limited input; provide more details for a refined score.",
        "principle_scores": principle_scores,
        "critical_factors": {
            "score_drivers_positive": drivers_pos,
            "score_drivers_negative": drivers_neg,
        },
        "qualitative_assessment": {
            "governance": "Add ownership, escalation, and change control to improve accountability.",
            "safety": "Validate safety filters, abuse monitoring, and rate limits.",
            "privacy": "Confirm data minimization, retention limits, and PII handling.",
            "fairness": "Check for biased training data and add evaluation slices.",
            "transparency": "Document intended use, limitations, and user messaging.",
        },
    }


def load_reference_architectures(limit: int = 5) -> List[Dict[str, Any]]:
    """Return reference architectures from the knowledge base (best-effort)."""

    kb_path = Path(__file__).parent / "knowledge" / "reference_architectures.json"
    if not kb_path.exists():
        return []

    try:
        data = json.loads(kb_path.read_text(encoding="utf-8"))
        results: List[Dict[str, Any]] = []
        for arch in data:
            repo = arch.get("repo") or {}
            results.append(
                {
                    "title": arch.get("title"),
                    "description": arch.get("description"),
                    "use_cases": arch.get("use_cases"),
                    "architecture_diagram": arch.get("architecture_diagram"),
                    "repo": repo.get("repo"),
                    "repo_description": repo.get("description"),
                }
            )
        return results[:limit]
    except Exception:
        return []


def compliance_links() -> Dict[str, Any]:
    """Curated compliance/RAI links per pillar."""

    return {
        "fairness": [
            "https://learn.microsoft.com/azure/machine-learning/concept-responsible-ai",
        ],
        "reliability_safety": [
            "https://learn.microsoft.com/azure/ai-services/content-safety/overview",
        ],
        "privacy_security": [
            "https://learn.microsoft.com/azure/security/fundamentals/overview",
        ],
        "transparency": [
            "https://learn.microsoft.com/azure/ai-services/openai/concepts/system-message",
        ],
        "inclusiveness": [
            "https://www.microsoft.com/ai/responsible-ai",
        ],
        "accountability": [
            "https://learn.microsoft.com/azure/ai-services/openai/concepts/responsible-use-guidelines",
        ],
    }


############################
# Server plumbing
############################


def list_tools() -> List[Dict[str, Any]]:
    return [
        {
            "name": "risk_score",
            "description": "Return deterministic risk scores for a project profile.",
            "input": {"type": "object", "properties": {"project_description": {"type": "string"}}},
        },
        {
            "name": "reference_architectures",
            "description": "List reference architectures from the knowledge base.",
            "input": {"type": "object", "properties": {"limit": {"type": "integer"}}},
        },
        {
            "name": "compliance_links",
            "description": "Return curated compliance and RAI links by pillar.",
            "input": {"type": "object"},
        },
    ]


def list_resources() -> List[Dict[str, Any]]:
    return [
        {
            "uri": "resource://rai/reference-architectures",
            "mimeType": "application/json",
            "description": "Curated reference architectures for RAI workloads.",
        },
        {
            "uri": "resource://rai/compliance-links",
            "mimeType": "application/json",
            "description": "Pillar-aligned compliance links.",
        },
    ]


def handle_call_tool(name: str, args: Dict[str, Any]) -> Any:
    if name == "risk_score":
        return calculate_basic_risk_scores(args or {})
    if name == "reference_architectures":
        limit = int(args.get("limit", 5)) if isinstance(args, dict) else 5
        return load_reference_architectures(limit=limit)
    if name == "compliance_links":
        return compliance_links()
    raise ValueError(f"Unknown tool: {name}")


def handle_read_resource(uri: str) -> Any:
    if uri == "resource://rai/reference-architectures":
        return load_reference_architectures(limit=20)
    if uri == "resource://rai/compliance-links":
        return compliance_links()
    raise ValueError(f"Unknown resource: {uri}")


def process_message(message: Dict[str, Any]) -> Dict[str, Any]:
    req_id = message.get("id")
    method = message.get("method")
    try:
        if method == "list_tools":
            return {"id": req_id, "result": list_tools()}
        if method == "list_resources":
            return {"id": req_id, "result": list_resources()}
        if method == "call_tool":
            params = message.get("params") or {}
            name = params.get("name")
            args = params.get("args", {})
            return {"id": req_id, "result": handle_call_tool(name, args)}
        if method == "read_resource":
            params = message.get("params") or {}
            uri = params.get("uri")
            return {"id": req_id, "result": handle_read_resource(uri)}
        return {"id": req_id, "error": {"code": -32601, "message": "Method not found"}}
    except Exception as exc:  # keep errors terse
        return {"id": req_id, "error": {"code": -32000, "message": str(exc)}}


def run_stdio_server() -> None:
    """Blocking stdio loop. Reads one JSON object per line and writes responses."""

    for raw in sys.stdin:
        raw = raw.strip()
        if not raw:
            continue
        try:
            message = json.loads(raw)
        except Exception:
            sys.stdout.write(json.dumps({"error": {"code": -32700, "message": "Parse error"}}) + "\n")
            sys.stdout.flush()
            continue

        response = process_message(message)
        sys.stdout.write(json.dumps(response) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    run_stdio_server()
