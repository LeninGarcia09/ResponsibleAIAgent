from flask import Flask, request, jsonify, make_response
from flask_cors import CORS, cross_origin
import uuid
import os
import json
import re
import logging
from datetime import datetime
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

app = Flask(__name__)
# Configure CORS with full options to ensure preflight works
CORS(app, origins="*", allow_headers=["Content-Type"], methods=["GET", "POST", "OPTIONS"])

logger = logging.getLogger(__name__)

# Global handler for OPTIONS preflight requests
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        response.headers.add("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        return response

# Import system prompt (legacy - kept for fallback)
from rai_system_prompt import SYSTEM_PROMPT, build_full_prompt, RESPONSE_FORMAT_INSTRUCTIONS, OPENAI_CONFIG

# Import adaptive prompt system (NEW - primary recommendation engine)
try:
    from adaptive_prompt_builder import get_adaptive_prompts
    from response_adapter import assess_and_configure, Priority, PriorityMapper
    ADAPTIVE_SYSTEM_AVAILABLE = True
    print("✓ Adaptive prompt system initialized")
except ImportError as e:
    ADAPTIVE_SYSTEM_AVAILABLE = False
    print(f"⚠ Adaptive prompt system not available, using legacy: {e}")

# Import knowledge loader for dynamic knowledge access
try:
    from knowledge_loader import get_knowledge_loader, get_latest_tools_summary
    knowledge_loader = get_knowledge_loader()
    KNOWLEDGE_AVAILABLE = True
    print("✓ Knowledge loader initialized")
except ImportError as e:
    KNOWLEDGE_AVAILABLE = False
    knowledge_loader = None
    print(f"⚠ Knowledge loader not available: {e}")

# Import dynamic resources fetcher for real-time reference architectures
try:
    from dynamic_resources import (
        get_dynamic_fetcher, 
        get_dynamic_reference_architectures,
        get_github_repo_realtime
    )
    DYNAMIC_RESOURCES_AVAILABLE = True
    print("✓ Dynamic resources fetcher initialized")
except ImportError as e:
    DYNAMIC_RESOURCES_AVAILABLE = False
    print(f"⚠ Dynamic resources not available: {e}")

    # Scenario matching metadata to personalize guidance
    SCENARIO_KEYWORD_HINTS = {
        "customer-chatbot": [
            "chatbot", "customer", "support", "helpdesk", "contact center",
            "call center", "service", "faq"
        ],
        "ai-agent-automation": [
            "agent", "automation", "workflow", "orchestrator", "autonomous",
            "action", "process"
        ],
        "loan-approval-model": [
            "loan", "credit", "underwriting", "finance", "mortgage", "lending"
        ],
        "content-generation-platform": [
            "content", "marketing", "copy", "generation", "creative", "social"
        ],
        "healthcare-ai-assistant": [
            "healthcare", "medical", "patient", "clinician", "doctor", "nurse"
        ],
        "rag-enterprise-search": [
            "rag", "retrieval", "search", "knowledge", "documents", "grounding"
        ],
        "image-generation-app": [
            "image", "vision", "generate", "art", "graphic", "media"
        ],
        "multi-agent-system": [
            "multi-agent", "swarm", "ensemble", "agents", "coordinator"
        ]
    }

    PROJECT_TYPE_HINTS = {
        "ai agent": ["ai-agent-automation", "multi-agent-system"],
        "ai-agent": ["ai-agent-automation", "multi-agent-system"],
        "ai agents": ["ai-agent-automation", "multi-agent-system"],
        "llm/generative ai": [
            "customer-chatbot", "content-generation-platform", "rag-enterprise-search"
        ],
        "generative ai": [
            "customer-chatbot", "content-generation-platform", "rag-enterprise-search"
        ],
        "llm": [
            "customer-chatbot", "content-generation-platform", "rag-enterprise-search"
        ],
        "traditional ml": ["loan-approval-model"],
        "ml": ["loan-approval-model"],
        "computer vision": ["image-generation-app"],
        "document intelligence": ["rag-enterprise-search"],
        "general ai": []
    }

    SCENARIO_STAKEHOLDERS = {
        "customer-chatbot": [
            "Customer Support Lead",
            "Security & Privacy Officer",
            "Responsible AI Champion"
        ],
        "ai-agent-automation": [
            "Operations Owner",
            "Identity & Access Lead",
            "Incident Response Manager"
        ],
        "loan-approval-model": [
            "Chief Risk Officer",
            "Compliance Lead",
            "Model Risk Management"
        ],
        "content-generation-platform": [
            "Marketing Director",
            "Brand Safety Owner",
            "Legal Counsel"
        ],
        "healthcare-ai-assistant": [
            "Clinical Safety Officer",
            "Privacy Officer",
            "Medical Governance Board"
        ],
        "rag-enterprise-search": [
            "Knowledge Management Lead",
            "Data Governance Officer",
            "Security Architect"
        ],
        "image-generation-app": [
            "Creative Director",
            "Intellectual Property Counsel",
            "Safety Reviewer"
        ],
        "multi-agent-system": [
            "Program Manager",
            "Security Operations",
            "Responsible AI Board"
        ]
    }

    DEFAULT_STAKEHOLDERS = [
        "Product Owner",
        "Responsible AI Champion",
        "Security & Privacy Lead",
        "Legal/Compliance Partner"
    ]


    def _safe_lower(value):
        return str(value).lower() if value else ""


    def _tokenize_for_matching(*values):
        text = " ".join(str(v) for v in values if v)
        tokens = set()
        for token in re.findall(r"[a-z0-9]+", text.lower()):
            if len(token) > 2:
                tokens.add(token)
        return tokens


    def _dedupe_preserve_order(items):
        seen = set()
        ordered = []
        for entry in items or []:
            if not entry:
                continue
            if entry in seen:
                continue
            seen.add(entry)
            ordered.append(entry)
        return ordered


    def _extract_latest_updates(research_result):
        updates = []
        if not isinstance(research_result, dict):
            return updates

        results = research_result.get("results")
        if isinstance(results, list):
            for item in results:
                if not isinstance(item, dict):
                    continue
                title = item.get("title") or item.get("headline") or item.get("name")
                summary = item.get("summary") or item.get("description") or item.get("excerpt")
                url = item.get("url") or item.get("link")
                if not url:
                    sources = item.get("sources")
                    if isinstance(sources, list) and sources:
                        url = sources[0]
                if not (title and url):
                    continue
                updates.append({
                    "title": title,
                    "summary": summary,
                    "url": url,
                    "last_verified": research_result.get("last_verified") or datetime.utcnow().date().isoformat()
                })

        if not updates:
            if isinstance(research_result.get("sources"), list):
                for source_url in research_result["sources"][:3]:
                    updates.append({
                        "title": "Latest resource",
                        "summary": research_result.get("raw_response"),
                        "url": source_url,
                        "last_verified": research_result.get("last_verified") or datetime.utcnow().date().isoformat()
                    })

        return updates[:5]


    def _format_tool_activity(tool_versions):
        if not isinstance(tool_versions, dict):
            return []

        activity = []
        for tool, details in tool_versions.items():
            if not isinstance(details, dict):
                continue
            activity.append({
                "tool": tool,
                "last_pushed": details.get("last_pushed"),
                "stars": details.get("stars"),
                "url": details.get("url")
            })

        activity.sort(key=lambda item: item.get("last_pushed") or "", reverse=True)
        return activity


    def _select_use_case_scenario(project_data, project_type_hint, ai_response):
        if not (KNOWLEDGE_AVAILABLE and knowledge_loader):
            return None

        catalog = knowledge_loader.tools_catalog or {}
        scenarios = catalog.get("actionable_use_cases", {}).get("scenarios", [])
        if not scenarios:
            return None

        combined_text = " ".join([
            project_data.get("project_name", ""),
            project_data.get("project_description", ""),
            project_data.get("additional_context", ""),
            project_data.get("business_problem", ""),
            project_data.get("intended_purpose", "")
        ]).lower()

        project_tokens = _tokenize_for_matching(
            project_data.get("project_name", ""),
            project_data.get("project_description", ""),
            project_data.get("additional_context", ""),
            project_data.get("business_problem", ""),
            project_data.get("intended_purpose", ""),
            project_data.get("technology_type", ""),
            " ".join(project_data.get("ai_capabilities", []) or [])
        )

        industry = _safe_lower(project_data.get("industry"))
        project_type_candidates = {
            _safe_lower(project_type_hint),
            _safe_lower(project_data.get("technology_type")),
            _safe_lower(ai_response.get("_adaptive_metadata", {}).get("detected_project_type"))
        }

        best_scenario = None
        best_score = 0

        for scenario in scenarios:
            scenario_id = scenario.get("id", "")
            scenario_tokens = _tokenize_for_matching(
                scenario.get("title", ""),
                scenario.get("description", ""),
                " ".join(scenario.get("industry_relevance", [])),
                scenario.get("risk_profile", "")
            )

            score = len(project_tokens & scenario_tokens)

            for hint in SCENARIO_KEYWORD_HINTS.get(scenario_id, []):
                if hint in combined_text:
                    score += 12

            if industry and any(industry in _safe_lower(ind) for ind in scenario.get("industry_relevance", [])):
                score += 10

            for project_type in project_type_candidates:
                if not project_type:
                    continue
                if scenario_id in PROJECT_TYPE_HINTS.get(project_type, []):
                    score += 14
                if project_type in scenario_tokens:
                    score += 4

            if score > best_score:
                best_score = score
                best_scenario = scenario

        if best_score < 6:
            return None

        return best_scenario


    def _parse_step(step_text):
        cleaned = (step_text or "").strip()
        if not cleaned:
            return "Implementation step", "Complete this step to advance your responsible AI readiness."

        cleaned = re.sub(r"^\s*\d+[\.|\)]\s*", "", cleaned)
        if ":" in cleaned:
            title, desc = cleaned.split(":", 1)
            return title.strip() or "Implementation step", desc.strip() or title.strip()

        return cleaned, cleaned


    def _build_week_one_checklist(steps):
        checklist = []
        for idx, raw_step in enumerate(steps[:4], start=1):
            title, desc = _parse_step(raw_step)
            checklist.append({
                "task": title,
                "priority": "High" if idx <= 2 else "Medium",
                "time_estimate": "1-2 days" if idx <= 2 else "3-4 days"
            })
        return checklist


    def _build_thirty_day_roadmap(steps):
        if not steps:
            return {}

        buckets = {
            "week_1": steps[:2],
            "week_2": steps[2:4],
            "week_3": steps[4:5],
            "week_4": steps[5:6]
        }

        roadmap = {}
        for week, bucket in buckets.items():
            if not bucket:
                continue
            titles = []
            descriptions = []
            for entry in bucket:
                title, desc = _parse_step(entry)
                titles.append(title)
                descriptions.append(desc)
            roadmap[week] = {
                "focus": titles[0],
                "actions": descriptions,
                "milestone": titles[-1]
            }
        return roadmap


    def _build_structured_steps(steps, quick_start_commands=None):
        structured = []
        for idx, raw_step in enumerate(steps[:4], start=1):
            title, desc = _parse_step(raw_step)
            entry = {
                "step": idx,
                "title": title,
                "description": desc
            }
            if quick_start_commands and idx == 2:
                entry["commands"] = quick_start_commands[:3]
            structured.append(entry)
        return structured

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT")  # e.g., https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")  # Your deployment name
AZURE_OPENAI_API_VERSION = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")

# Initialize Azure OpenAI client with Managed Identity
client = None
auth_method = None

try:
    if AZURE_OPENAI_ENDPOINT:
        # Use Managed Identity (DefaultAzureCredential)
        # This works with: Managed Identity, Azure CLI, VS Code, etc.
        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(),
            "https://cognitiveservices.azure.com/.default"
        )
        
        client = AzureOpenAI(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            azure_ad_token_provider=token_provider,
            api_version=AZURE_OPENAI_API_VERSION
        )
        auth_method = "managed_identity"
        print(f"✓ Azure OpenAI initialized with Managed Identity")
        print(f"  Endpoint: {AZURE_OPENAI_ENDPOINT}")
        print(f"  Deployment: {AZURE_OPENAI_DEPLOYMENT}")
    else:
        print("⚠ AZURE_OPENAI_ENDPOINT not set - AI features disabled")
except Exception as e:
    print(f"✗ Failed to initialize Azure OpenAI: {e}")
    client = None

# Comprehensive Microsoft Responsible AI Tools & Resources
MICROSOFT_RAI_TOOLS = {
    "fairness": [
        {
            "name": "Fairlearn",
            "url": "https://fairlearn.org/",
            "description": "Open-source toolkit for assessing and improving fairness of AI systems. Includes metrics for group fairness and algorithms for mitigating unfairness.",
            "category": "Assessment & Mitigation"
        },
        {
            "name": "Azure Machine Learning Responsible AI Dashboard",
            "url": "https://learn.microsoft.com/azure/machine-learning/concept-responsible-ai-dashboard",
            "description": "Unified interface for model debugging, fairness assessment, error analysis, and interpretability in Azure ML.",
            "category": "Dashboard & Visualization"
        },
        {
            "name": "InterpretML",
            "url": "https://interpret.ml/",
            "description": "Microsoft's toolkit for training interpretable models and explaining blackbox systems.",
            "category": "Explainability"
        }
    ],
    "safety": [
        {
            "name": "Azure AI Content Safety",
            "url": "https://azure.microsoft.com/products/ai-services/ai-content-safety",
            "description": "Detect harmful content including hate speech, violence, self-harm, and sexual content in text and images.",
            "category": "Content Moderation"
        },
        {
            "name": "Azure OpenAI Content Filtering",
            "url": "https://learn.microsoft.com/azure/ai-services/openai/concepts/content-filter",
            "description": "Built-in content filtering for Azure OpenAI deployments to block harmful inputs and outputs.",
            "category": "Content Filtering"
        },
        {
            "name": "Prompt Shields",
            "url": "https://learn.microsoft.com/azure/ai-services/content-safety/concepts/jailbreak-detection",
            "description": "Detect and block prompt injection and jailbreak attempts in LLM applications.",
            "category": "Security"
        },
        {
            "name": "Groundedness Detection",
            "url": "https://learn.microsoft.com/azure/ai-services/content-safety/concepts/groundedness",
            "description": "Detect hallucinations and ungrounded content in LLM outputs.",
            "category": "Accuracy & Reliability"
        },
        {
            "name": "Azure AI Studio Safety Evaluations",
            "url": "https://learn.microsoft.com/azure/ai-studio/concepts/evaluation-approach-gen-ai",
            "description": "Evaluate generative AI applications for safety, quality, and performance.",
            "category": "Evaluation"
        }
    ],
    "privacy": [
        {
            "name": "Presidio",
            "url": "https://microsoft.github.io/presidio/",
            "description": "Data protection and PII anonymization SDK. Detect and redact sensitive information in text and images.",
            "category": "PII Detection & Anonymization"
        },
        {
            "name": "SmartNoise",
            "url": "https://github.com/opendp/smartnoise-sdk",
            "description": "Differential privacy library for protecting individual privacy in data analysis.",
            "category": "Differential Privacy"
        },
        {
            "name": "Azure Confidential Computing",
            "url": "https://azure.microsoft.com/solutions/confidential-compute/",
            "description": "Protect data in use with hardware-based trusted execution environments.",
            "category": "Data Protection"
        },
        {
            "name": "Customer Lockbox",
            "url": "https://learn.microsoft.com/azure/security/fundamentals/customer-lockbox-overview",
            "description": "Control and audit Microsoft support access to your data.",
            "category": "Access Control"
        }
    ],
    "transparency": [
        {
            "name": "InterpretML / Explainable Boosting Machine",
            "url": "https://interpret.ml/",
            "description": "Glass-box models that are inherently interpretable while maintaining high accuracy.",
            "category": "Interpretable Models"
        },
        {
            "name": "SHAP (via InterpretML)",
            "url": "https://github.com/interpretml/interpret",
            "description": "SHapley Additive exPlanations for understanding feature contributions.",
            "category": "Model Explanation"
        },
        {
            "name": "Error Analysis",
            "url": "https://erroranalysis.ai/",
            "description": "Identify and diagnose model errors with tree-based error exploration.",
            "category": "Error Analysis"
        },
        {
            "name": "Azure OpenAI System Message Best Practices",
            "url": "https://learn.microsoft.com/azure/ai-services/openai/concepts/system-message",
            "description": "Guidelines for transparent system prompts in LLM applications.",
            "category": "LLM Transparency"
        },
        {
            "name": "Model Cards",
            "url": "https://learn.microsoft.com/azure/machine-learning/concept-model-card",
            "description": "Document model purpose, performance, limitations, and intended use.",
            "category": "Documentation"
        }
    ],
    "accountability": [
        {
            "name": "Azure Machine Learning MLOps",
            "url": "https://learn.microsoft.com/azure/machine-learning/concept-model-management-and-deployment",
            "description": "End-to-end ML lifecycle management with versioning, lineage, and governance.",
            "category": "ML Lifecycle"
        },
        {
            "name": "Azure Purview / Microsoft Purview",
            "url": "https://azure.microsoft.com/products/purview/",
            "description": "Unified data governance for discovering, cataloging, and managing data assets.",
            "category": "Data Governance"
        },
        {
            "name": "Azure Policy",
            "url": "https://learn.microsoft.com/azure/governance/policy/overview",
            "description": "Enforce organizational standards and assess compliance at scale.",
            "category": "Compliance"
        },
        {
            "name": "Microsoft Responsible AI Impact Assessment Template",
            "url": "https://learn.microsoft.com/azure/machine-learning/concept-responsible-ai",
            "description": "Framework for assessing potential impacts of AI systems.",
            "category": "Assessment Framework"
        }
    ],
    "security": [
        {
            "name": "Azure AI Studio Red Teaming",
            "url": "https://learn.microsoft.com/azure/ai-studio/concepts/red-teaming",
            "description": "Adversarial testing tools for identifying vulnerabilities in AI systems.",
            "category": "Security Testing"
        },
        {
            "name": "Counterfit",
            "url": "https://github.com/Azure/counterfit",
            "description": "Microsoft's tool for security testing of AI systems against adversarial attacks.",
            "category": "Adversarial ML"
        },
        {
            "name": "Azure Key Vault",
            "url": "https://azure.microsoft.com/products/key-vault/",
            "description": "Secure storage for API keys, secrets, and certificates.",
            "category": "Secrets Management"
        },
        {
            "name": "Microsoft Defender for Cloud",
            "url": "https://azure.microsoft.com/products/defender-for-cloud/",
            "description": "Cloud security posture management and threat protection.",
            "category": "Cloud Security"
        }
    ],
    "llm_specific": [
        {
            "name": "Azure OpenAI Service",
            "url": "https://azure.microsoft.com/products/ai-services/openai-service/",
            "description": "Enterprise-grade OpenAI models with built-in responsible AI features.",
            "category": "LLM Platform"
        },
        {
            "name": "Semantic Kernel",
            "url": "https://learn.microsoft.com/semantic-kernel/",
            "description": "SDK for integrating LLMs with conventional programming, includes prompt management and planning.",
            "category": "LLM Development"
        },
        {
            "name": "Prompt Flow",
            "url": "https://learn.microsoft.com/azure/ai-studio/how-to/prompt-flow",
            "description": "Development tool for building, evaluating, and deploying LLM applications.",
            "category": "LLM Development"
        },
        {
            "name": "Azure AI Evaluation SDK",
            "url": "https://learn.microsoft.com/azure/ai-studio/how-to/develop/evaluate-sdk",
            "description": "Programmatic evaluation of LLM applications for quality and safety.",
            "category": "LLM Evaluation"
        }
    ]
}

# Microsoft RAI Principles and Best Practices
MICROSOFT_RAI_PRINCIPLES = {
    "fairness": {
        "title": "Fairness",
        "description": "AI systems should treat all people fairly and avoid affecting similarly situated groups in different ways.",
        "key_questions": [
            "Who might be affected by this system?",
            "What demographic groups should be considered?",
            "How will performance be measured across groups?",
            "What is the acceptable disparity threshold?"
        ],
        "best_practices": [
            "Identify and document potential sources of bias in training data",
            "Test model performance across demographic groups before deployment",
            "Implement ongoing monitoring for fairness metrics in production",
            "Establish clear remediation processes for detected bias",
            "Include diverse perspectives in design and testing phases"
        ]
    },
    "reliability_safety": {
        "title": "Reliability & Safety",
        "description": "AI systems should perform reliably and safely under expected conditions and handle unexpected conditions gracefully.",
        "key_questions": [
            "What are the failure modes and their consequences?",
            "How will the system behave with out-of-distribution inputs?",
            "What human oversight is required?",
            "How quickly can the system be disabled if needed?"
        ],
        "best_practices": [
            "Define operational boundaries and document limitations",
            "Implement robust error handling and fallback mechanisms",
            "Conduct adversarial testing and red team exercises",
            "Establish human-in-the-loop processes for high-stakes decisions",
            "Create incident response and rollback procedures"
        ]
    },
    "privacy_security": {
        "title": "Privacy & Security",
        "description": "AI systems should be secure and respect privacy throughout their lifecycle.",
        "key_questions": [
            "What data is collected and how is it used?",
            "How is sensitive data protected?",
            "Who has access to the data and model?",
            "How long is data retained?"
        ],
        "best_practices": [
            "Apply data minimization principles - collect only what's needed",
            "Implement encryption for data at rest and in transit",
            "Use differential privacy techniques when appropriate",
            "Conduct regular security assessments and penetration testing",
            "Establish clear data retention and deletion policies"
        ]
    },
    "inclusiveness": {
        "title": "Inclusiveness",
        "description": "AI systems should empower everyone and engage people, including those with disabilities.",
        "key_questions": [
            "Does the system work for users with different abilities?",
            "Are there language or cultural barriers?",
            "How accessible is the system's interface?",
            "Who might be excluded by design choices?"
        ],
        "best_practices": [
            "Follow accessibility standards (WCAG) in interface design",
            "Test with diverse user groups including people with disabilities",
            "Support multiple languages and cultural contexts where appropriate",
            "Avoid requiring capabilities that exclude potential users",
            "Gather feedback from underrepresented groups"
        ]
    },
    "transparency": {
        "title": "Transparency",
        "description": "AI systems should be understandable, with clear documentation of capabilities and limitations.",
        "key_questions": [
            "Do users know they're interacting with AI?",
            "Can decisions be explained?",
            "Are limitations clearly documented?",
            "How is the system's behavior logged?"
        ],
        "best_practices": [
            "Clearly disclose AI involvement to users",
            "Provide explanations for AI-driven decisions when appropriate",
            "Maintain comprehensive documentation (model cards, datasheets)",
            "Log system behavior for auditability",
            "Communicate known limitations to stakeholders"
        ]
    },
    "accountability": {
        "title": "Accountability",
        "description": "People should be accountable for AI systems, with clear governance and oversight.",
        "key_questions": [
            "Who is responsible for the system's behavior?",
            "What governance processes are in place?",
            "How are concerns escalated and addressed?",
            "What mechanisms exist for feedback and redress?"
        ],
        "best_practices": [
            "Establish clear ownership and accountability chains",
            "Implement governance review processes before deployment",
            "Create mechanisms for users to report issues and seek redress",
            "Maintain audit trails of decisions and changes",
            "Conduct regular reviews and impact assessments"
        ]
    }
}


def augment_with_dynamic_resources(ai_response: dict, project_data: dict) -> dict:
    """Augment the response with dynamic resources and knowledge-backed context."""
    if not DYNAMIC_RESOURCES_AVAILABLE:
        return ai_response

    try:
        fetcher = get_dynamic_fetcher(client) if DYNAMIC_RESOURCES_AVAILABLE else None
        project_type_source = (
            ai_response.get("detected_project_type")
            or ai_response.get("_adaptive_metadata", {}).get("detected_project_type")
            or project_data.get("technology_type", "")
        )
        project_type = _safe_lower(project_type_source)
        use_case = project_data.get("project_description", "")[:200]

        scenario = _select_use_case_scenario(project_data, project_type_source, ai_response)

        dynamic_archs = get_dynamic_reference_architectures(project_type, use_case)
        dynamic_repos = dynamic_archs.get("github_repos", []) or dynamic_archs.get("repos", [])
        quick_start_commands = dynamic_archs.get("quick_start_commands", [])

        latest_updates = []
        latest_tool_activity = []

        if fetcher:
            try:
                topic = scenario.get("title") if scenario else project_type_source or project_data.get("project_name", "Responsible AI")
                research_query = f"{topic} Microsoft responsible AI updates {datetime.utcnow().year}"
                research_result = fetcher.search_with_bing_grounding(
                    query=research_query,
                    context="Microsoft responsible AI tools, governance, and safety"
                )
                latest_updates = _extract_latest_updates(research_result)
            except Exception as research_error:
                logger.debug(f"Latest updates lookup failed: {research_error}")

            try:
                tool_versions = fetcher.get_latest_tools_versions()
                latest_tool_activity = _format_tool_activity(tool_versions)
            except Exception as activity_error:
                logger.debug(f"Latest tool activity lookup failed: {activity_error}")

        fallback_risks = calculate_basic_risk_scores(project_data)
        risk_scores = ai_response.get("risk_scores")

        if not risk_scores:
            ai_response["risk_scores"] = fallback_risks
            risk_scores = ai_response["risk_scores"]
        else:
            risk_scores.setdefault("overall_score", fallback_risks.get("overall_score"))
            risk_scores.setdefault("risk_level", fallback_risks.get("risk_level"))

            summary_parts = []
            if scenario and scenario.get("risk_profile"):
                summary_parts.append(f"Scenario assessment: {scenario['risk_profile']}")
            if risk_scores.get("risk_summary"):
                summary_parts.append(risk_scores["risk_summary"])
            else:
                summary_parts.append(fallback_risks.get("risk_summary"))
            risk_scores["risk_summary"] = " ".join(part for part in summary_parts if part).strip()

            principle_scores = risk_scores.get("principle_scores")
            if not principle_scores:
                risk_scores["principle_scores"] = fallback_risks.get("principle_scores", {})
            else:
                for principle, score in fallback_risks.get("principle_scores", {}).items():
                    principle_scores.setdefault(principle, score)

            existing_factors = risk_scores.setdefault("critical_factors", {})
            fallback_factors = fallback_risks.get("critical_factors", {})
            for factor_key in ["score_drivers_positive", "score_drivers_negative"]:
                merged = _dedupe_preserve_order(
                    (existing_factors.get(factor_key) or []) + (fallback_factors.get(factor_key) or [])
                )
                if merged:
                    existing_factors[factor_key] = merged

            if not risk_scores.get("qualitative_assessment"):
                risk_scores["qualitative_assessment"] = fallback_risks.get("qualitative_assessment")

            if not risk_scores.get("score_explanation"):
                drivers = existing_factors.get("score_drivers_negative", [])
                driver_clause = ""
                if drivers:
                    driver_clause = f"Key drivers: {', '.join(drivers[:2])}"
                if scenario and scenario.get("risk_profile"):
                    risk_scores["score_explanation"] = " ".join(
                        part for part in [scenario["risk_profile"], driver_clause] if part
                    ).strip()
                elif driver_clause:
                    risk_scores["score_explanation"] = driver_clause

        reference_description = dynamic_archs.get(
            "description",
            f"Reference architecture for {scenario.get('title') if scenario else (project_type_source or 'AI')} projects"
        )

        if not ai_response.get("reference_architecture") or not ai_response["reference_architecture"].get("repos"):
            ai_response["reference_architecture"] = {
                "description": reference_description,
                "azure_services": dynamic_archs.get("azure_services", [
                    "Azure OpenAI Service",
                    "Azure AI Studio",
                    "Azure Machine Learning",
                    "Azure Content Safety"
                ]),
                "repos": [
                    {
                        "name": repo.get("name", ""),
                        "url": repo.get("url", repo.get("html_url", "")),
                        "description": repo.get("description", ""),
                        "stars": repo.get("stars", repo.get("stargazers_count", 0)),
                        "language": repo.get("language", "Python"),
                        "last_updated": repo.get("last_updated", repo.get("updated_at", ""))
                    }
                    for repo in dynamic_repos[:5]
                ],
                "patterns": dynamic_archs.get("patterns", []),
                "documentation": dynamic_archs.get("documentation", []),
                "microsoft_docs": dynamic_archs.get("microsoft_docs", [
                    {
                        "title": "Azure AI Services Documentation",
                        "url": "https://learn.microsoft.com/azure/ai-services/"
                    },
                    {
                        "title": "Responsible AI Overview",
                        "url": "https://learn.microsoft.com/azure/machine-learning/concept-responsible-ai"
                    },
                    {
                        "title": "Azure OpenAI Service",
                        "url": "https://learn.microsoft.com/azure/ai-services/openai/"
                    }
                ])
            }

        quick_start_guide = ai_response.get("quick_start_guide") or {}
        ai_response["quick_start_guide"] = quick_start_guide

        quick_start_summary = ai_response.get("quick_start") or {}
        ai_response["quick_start"] = quick_start_summary

        if latest_updates and not quick_start_guide.get("latest_updates"):
            quick_start_guide["latest_updates"] = latest_updates
        if latest_updates and not ai_response.get("latest_resources"):
            ai_response["latest_resources"] = latest_updates
        if latest_tool_activity and not quick_start_guide.get("latest_tool_activity"):
            quick_start_guide["latest_tool_activity"] = latest_tool_activity
        if latest_tool_activity and not quick_start_summary.get("latest_tool_activity"):
            quick_start_summary["latest_tool_activity"] = latest_tool_activity[:3]

        scenario_tool_lookup = {}
        essential_tools = []

        if scenario:
            for group in ("required_tools", "recommended_tools"):
                for entry in scenario.get(group, []):
                    name = entry.get("tool") or entry.get("name")
                    if not name:
                        continue
                    lowered = name.lower()
                    scenario_tool_lookup.setdefault(lowered, entry)
                    tool_details = knowledge_loader.get_tool_info(name) if KNOWLEDGE_AVAILABLE and knowledge_loader else {}
                    doc_url = entry.get("url") or (tool_details or {}).get("documentation_url") or (tool_details or {}).get("url", "")
                    purpose = entry.get("purpose") or (tool_details or {}).get("primary_purpose") or (tool_details or {}).get("description", "")
                    tool_payload = {
                        "name": name,
                        "url": doc_url,
                        "purpose": purpose or "Supports responsible AI controls for this scenario."
                    }
                    install_command = (tool_details or {}).get("install_command")
                    if install_command:
                        tool_payload["install_command"] = install_command
                    essential_tools.append(tool_payload)

            if essential_tools and not quick_start_guide.get("essential_tools"):
                quick_start_guide["essential_tools"] = essential_tools[:6]

            scenario_steps = scenario.get("implementation_steps", [])
            if scenario_steps:
                if not quick_start_guide.get("week_one_checklist"):
                    quick_start_guide["week_one_checklist"] = _build_week_one_checklist(scenario_steps)
                if not quick_start_guide.get("thirty_day_roadmap"):
                    roadmap = _build_thirty_day_roadmap(scenario_steps)
                    if roadmap:
                        quick_start_guide["thirty_day_roadmap"] = roadmap
                if not quick_start_guide.get("steps"):
                    quick_start_guide["steps"] = _build_structured_steps(scenario_steps, quick_start_commands)

            if scenario and not quick_start_guide.get("quick_reference"):
                quick_reference = {
                    "top_3_tools": _dedupe_preserve_order([
                        entry.get("tool") or entry.get("name")
                        for entry in scenario.get("required_tools", [])
                    ])[:3],
                    "key_metrics": scenario.get("success_metrics", [])[:4],
                    "red_flags": scenario.get("common_pitfalls", [])[:4],
                    "stakeholders_to_involve": _dedupe_preserve_order(
                        SCENARIO_STAKEHOLDERS.get(scenario.get("id"), []) + DEFAULT_STAKEHOLDERS
                    )[:5]
                }
                quick_start_guide["quick_reference"] = {
                    key: value for key, value in quick_reference.items() if value
                }

            if not quick_start_guide.get("templates_and_checklists"):
                quick_start_guide["templates_and_checklists"] = [
                    {
                        "name": "Microsoft Responsible AI Standard",
                        "url": "https://learn.microsoft.com/ai/responsible-ai/responsible-ai-standard",
                        "purpose": "Baseline guardrails and accountability requirements"
                    },
                    {
                        "name": "Responsible AI Impact Assessment",
                        "url": "https://aka.ms/rai-impact-assessment",
                        "purpose": "Document risks, mitigations, and approvals for this solution"
                    }
                ]

            quick_start_guide.setdefault(
                "detected_project_type",
                scenario.get("title") or project_type_source or "AI Solution"
            )
            if scenario.get("risk_profile"):
                quick_start_guide["risk_profile"] = scenario["risk_profile"]
            if scenario.get("title"):
                quick_start_guide["scenario_title"] = scenario["title"]

            if essential_tools:
                quick_start_summary["essential_tools"] = essential_tools[:3]
            if quick_start_guide.get("week_one_checklist"):
                quick_start_summary["first_week_actions"] = [
                    item["task"] for item in quick_start_guide["week_one_checklist"][:4]
                ]
            quick_start_summary.setdefault(
                "reference_architecture",
                ai_response.get("reference_architecture", {}).get("description", reference_description)
            )
            if dynamic_repos:
                quick_start_summary["starter_repo"] = dynamic_repos[0].get("url", dynamic_repos[0].get("html_url", ""))
            else:
                quick_start_summary.setdefault("starter_repo", "https://github.com/microsoft/responsible-ai-toolbox")
            if scenario.get("risk_profile"):
                quick_start_summary["risk_profile"] = scenario["risk_profile"]
            if scenario.get("title"):
                quick_start_summary["scenario"] = scenario["title"]

            pillar_recs = ai_response.get("recommendations_by_pillar")
            if isinstance(pillar_recs, dict):
                fallback_gap = (
                    scenario.get("common_pitfalls", [])[:1] or [fallback_risks.get("risk_summary")]
                )[0]
                for pillar_key, pillar_data in pillar_recs.items():
                    if not isinstance(pillar_data, dict):
                        continue
                    pillar_data.setdefault(
                        "why_it_matters",
                        scenario.get("risk_profile", pillar_data.get("pillar_description", ""))
                    )
                    pillar_data.setdefault("risk_if_ignored", fallback_gap)
                    recommendations = pillar_data.get("recommendations", [])
                    if not isinstance(recommendations, list):
                        continue
                    for rec in recommendations:
                        if not isinstance(rec, dict):
                            continue
                        tool_entry = rec.get("tool")
                        tool_name = None
                        if isinstance(tool_entry, dict):
                            tool_name = tool_entry.get("name")
                        elif isinstance(tool_entry, str):
                            tool_name = tool_entry
                        tool_lookup = scenario_tool_lookup.get(_safe_lower(tool_name)) if tool_name else None
                        tool_metadata = {}
                        if tool_name and KNOWLEDGE_AVAILABLE and knowledge_loader:
                            tool_metadata = knowledge_loader.get_tool_info(tool_name) or {}

                        if not rec.get("why_needed"):
                            if tool_lookup and tool_lookup.get("purpose"):
                                rec["why_needed"] = tool_lookup["purpose"]
                            elif scenario.get("risk_profile"):
                                rec["why_needed"] = scenario["risk_profile"]
                            else:
                                rec["why_needed"] = fallback_risks.get("risk_summary")

                        if not rec.get("what_happens_without"):
                            rec["what_happens_without"] = fallback_gap

                        if tool_name:
                            normalized_tool = tool_entry if isinstance(tool_entry, dict) else {"name": tool_name}
                            if tool_lookup and tool_lookup.get("purpose"):
                                normalized_tool.setdefault("purpose", tool_lookup.get("purpose"))
                            if tool_lookup and tool_lookup.get("configuration"):
                                normalized_tool.setdefault("how_it_helps", tool_lookup.get("configuration"))
                            if tool_metadata:
                                normalized_tool.setdefault(
                                    "purpose",
                                    tool_metadata.get("primary_purpose") or tool_metadata.get("description", "")
                                )
                                normalized_tool.setdefault(
                                    "url",
                                    tool_metadata.get("documentation_url") or tool_metadata.get("url", "")
                                )
                                if tool_metadata.get("primary_purpose"):
                                    normalized_tool.setdefault("how_it_helps", tool_metadata.get("primary_purpose"))
                            rec["tool"] = normalized_tool

                        if (
                            not rec.get("implementation_steps")
                            or not isinstance(rec.get("implementation_steps"), list)
                        ) and scenario.get("implementation_steps"):
                            rec["implementation_steps"] = scenario["implementation_steps"][:3]

        if not quick_start_guide.get("steps") and not scenario:
            quick_start_guide["title"] = f"Getting Started with {(project_type_source or 'AI').upper()} Development"
            quick_start_guide["description"] = "Essential steps to set up your responsible AI project"
            quick_start_guide["steps"] = _build_structured_steps([
                "1. Set up Azure AI environment",
                "2. Install required libraries",
                "3. Configure content safety controls",
                "4. Implement responsible AI practices"
            ], quick_start_commands)
            quick_start_guide.setdefault(
                "resources",
                dynamic_archs.get("documentation", dynamic_archs.get("microsoft_docs", [
                    {
                        "title": "Azure AI Quickstart",
                        "url": "https://learn.microsoft.com/azure/ai-services/openai/quickstart"
                    },
                    {
                        "title": "Responsible AI Toolbox",
                        "url": "https://github.com/microsoft/responsible-ai-toolbox"
                    }
                ]))
            )
            quick_start_guide.setdefault(
                "starter_repos",
                [
                    {
                        "name": repo.get("name", ""),
                        "url": repo.get("url", repo.get("html_url", "")),
                        "clone_command": f"git clone {repo.get('url', repo.get('html_url', ''))}.git"
                    }
                    for repo in dynamic_repos[:3]
                ]
            )

        if not quick_start_summary.get("essential_tools"):
            quick_start_summary["essential_tools"] = quick_start_guide.get("essential_tools", [
                {
                    "name": "Azure Content Safety",
                    "url": "https://learn.microsoft.com/azure/ai-services/content-safety/",
                    "purpose": "Content moderation and safety filtering"
                },
                {
                    "name": "Responsible AI Toolbox",
                    "url": "https://github.com/microsoft/responsible-ai-toolbox",
                    "purpose": "Fairness assessment and model debugging"
                },
                {
                    "name": "Prompt Flow",
                    "url": "https://github.com/microsoft/promptflow",
                    "purpose": "LLM application development and testing"
                }
            ])

        if not quick_start_summary.get("first_week_actions"):
            quick_start_summary["first_week_actions"] = [
                "Set up Azure OpenAI with content filtering",
                "Configure Azure AI Content Safety for user interactions",
                "Install Fairlearn and run a baseline bias assessment",
                "Enable monitoring with Azure Application Insights"
            ]

        if not quick_start_summary.get("reference_architecture"):
            quick_start_summary["reference_architecture"] = ai_response.get("reference_architecture", {}).get(
                "description",
                dynamic_archs.get(
                    "description",
                    f"Azure AI + Content Safety architecture for {project_type_source or 'AI'} applications"
                )
            )

        if not quick_start_summary.get("starter_repo"):
            quick_start_summary["starter_repo"] = (
                dynamic_repos[0].get("url", dynamic_repos[0].get("html_url", ""))
                if dynamic_repos else "https://github.com/microsoft/responsible-ai-toolbox"
            )

        return ai_response

    except Exception as e:
        print(f"⚠ Error augmenting with dynamic resources: {e}")
        return ai_response


def calculate_basic_risk_scores(project_data: dict) -> dict:
    """Generate a simple risk score when the model omits it.

    This keeps the UI populated with the expected structure and gives users
    a starting point until the adaptive model returns detailed scores.
    """

    overall = 55
    drivers_pos = []
    drivers_neg = []

    stage = (project_data.get("deployment_stage") or "").lower()
    description = (project_data.get("project_description") or "").lower()
    tech_type = (project_data.get("technology_type") or "").lower()
    industry = (project_data.get("industry") or "").lower()
    capabilities = project_data.get("ai_capabilities") or []

    def bump(amount: int, reason: str, positive: bool = False):
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

    # Guardrails: keep score bounded
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


def build_static_pillar_recommendations(recommendations: list) -> dict:
    """Create a minimal pillar-organized structure from static recommendations."""

    icon_map = {
        "reliability_safety": "🛡️",
        "privacy_security": "🔒",
        "fairness": "⚖️",
        "transparency": "🔍",
        "inclusiveness": "🌍",
        "accountability": "📋",
    }

    key_map = {
        "fairness": "fairness",
        "reliability & safety": "reliability_safety",
        "privacy & security": "privacy_security",
        "transparency": "transparency",
        "inclusiveness": "inclusiveness",
        "accountability": "accountability",
        "llm/generative ai specific": "reliability_safety",
        "llm generative ai specific": "reliability_safety",
    }

    pillars = {}

    for rec in recommendations:
        principle = (rec.get("principle") or "").strip()
        principle_key = key_map.get(principle.lower()) or "_".join(principle.lower().replace("&", "").split())
        if not principle_key:
            continue

        if principle_key not in pillars:
            pillars[principle_key] = {
                "pillar_name": principle or principle_key.replace("_", " ").title(),
                "pillar_icon": icon_map.get(principle_key, "📌"),
                "pillar_description": rec.get("description", ""),
                "why_it_matters": rec.get("description", ""),
                "risk_if_ignored": "Higher risk posture if these controls are not implemented.",
                "recommendations": [],
            }

        for item in rec.get("recommendations", []):
            pillars[principle_key]["recommendations"].append({
                "title": item,
                "why_needed": rec.get("description", ""),
                "what_happens_without": "Increased likelihood of safety, fairness, or privacy issues if left unaddressed.",
                "priority": rec.get("priority", "High"),
            })

    return pillars


def generate_recommendations_adaptive(project_data):
    """
    Generate recommendations using the adaptive prompt system.
    
    This function:
    1. Assesses input completeness
    2. Builds adapted system and user prompts
    3. Calls Azure OpenAI with the appropriate context
    4. Returns structured recommendations with priority levels
    """
    if not client:
        return generate_recommendations_static(project_data)
    
    if not ADAPTIVE_SYSTEM_AVAILABLE:
        # Fall back to legacy system
        return generate_recommendations_with_ai_legacy(project_data)
    
    try:
        # Get adaptive prompts based on input assessment
        adaptive_result = get_adaptive_prompts(project_data)
        
        system_prompt = adaptive_result["system_prompt"]
        user_prompt = adaptive_result["user_prompt"]
        response_config = adaptive_result["response_config"]
        input_assessment = adaptive_result["input_assessment"]
        
        # Call Azure OpenAI with adapted prompts
        response = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            temperature=OPENAI_CONFIG["temperature"],
            max_tokens=OPENAI_CONFIG["max_tokens"],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        # Parse the response
        ai_response = json.loads(response.choices[0].message.content)
        
        # Enrich response with adaptive metadata
        ai_response["_adaptive_metadata"] = {
            "response_depth": response_config["response_depth"],
            "review_mode": response_config["review_mode"],
            "completeness_score": input_assessment["completeness_score"],
            "detected_project_type": response_config["project_type"],
            "suggestions_for_better_review": input_assessment.get("suggestions", []),
            "enablement_message": response_config.get("enablement_message", "")
        }
        
        return ai_response
        
    except Exception as e:
        print(f"Adaptive recommendation error: {e}")
        # Fall back to legacy system
        return generate_recommendations_with_ai_legacy(project_data)


def generate_recommendations_with_ai_legacy(project_data, is_advanced=False):
    """Legacy recommendation generation using Azure OpenAI (fallback)."""
    if not client:
        return generate_recommendations_static(project_data)
    
    try:
        # Build the user prompt with project details
        if is_advanced:
            user_prompt = build_advanced_prompt(project_data)
        else:
            user_prompt = build_full_prompt(
                project_name=project_data.get("project_name", "Unknown Project"),
                project_description=project_data.get("project_description", ""),
                deployment_stage=project_data.get("deployment_stage", "Development"),
                technology_type=project_data.get("technology_type", "Not specified"),
                industry=project_data.get("industry", "Not specified"),
                target_users=project_data.get("target_users", "Not specified"),
                data_types=project_data.get("data_types", "Not specified"),
                additional_context=project_data.get("additional_context", "")
            )
        
        # Call Azure OpenAI using the deployment name
        response = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,  # This is the deployment name in Azure
            temperature=OPENAI_CONFIG["temperature"],
            max_tokens=OPENAI_CONFIG["max_tokens"],
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        # Parse the response
        ai_response = json.loads(response.choices[0].message.content)
        return ai_response
        
    except Exception as e:
        print(f"OpenAI API error: {e}")
        # Fallback to static recommendations
        return {"error": str(e), "fallback": True, "recommendations": generate_recommendations_static(project_data)}


def build_advanced_prompt(project_data):
    """Build a comprehensive prompt from the advanced review questionnaire."""
    sections = []
    
    # Project Overview
    sections.append(f"""## Project Overview
- **Project Name**: {project_data.get('project_name', 'Not provided')}
- **Deployment Stage**: {project_data.get('deployment_stage', 'Not specified')}""")
    
    # Purpose & Use Case
    if any(project_data.get(f) for f in ['intended_purpose', 'business_problem', 'end_users']):
        sections.append(f"""## Purpose & Use Case
- **Intended Purpose**: {project_data.get('intended_purpose', 'Not provided')}
- **Business Problem**: {project_data.get('business_problem', 'Not provided')}
- **End Users**: {project_data.get('end_users', 'Not provided')}""")
    
    # Data & Inputs
    if any(project_data.get(f) for f in ['data_sources', 'data_collection_storage', 'sensitive_data']):
        sections.append(f"""## Data & Inputs
- **Data Sources**: {project_data.get('data_sources', 'Not provided')}
- **Data Collection, Storage & Processing**: {project_data.get('data_collection_storage', 'Not provided')}
- **Sensitive/Personal Data**: {project_data.get('sensitive_data', 'Not provided')}""")
    
    # Model & Technology
    if any(project_data.get(f) for f in ['ai_models', 'model_type', 'environments_connectors']):
        sections.append(f"""## Model & Technology
- **AI Models/Techniques**: {project_data.get('ai_models', 'Not provided')}
- **Model Type**: {project_data.get('model_type', 'Not specified')}
- **Environments & Connectors**: {project_data.get('environments_connectors', 'Not provided')}""")
    
    # Fairness & Bias
    if any(project_data.get(f) for f in ['bias_checking', 'bias_mitigation']):
        sections.append(f"""## Fairness & Bias
- **Bias Detection Methods**: {project_data.get('bias_checking', 'Not provided')}
- **Mitigation Strategies**: {project_data.get('bias_mitigation', 'Not provided')}""")
    
    # Transparency & Explainability
    if any(project_data.get(f) for f in ['decision_explainability', 'output_documentation']):
        sections.append(f"""## Transparency & Explainability
- **Decision Explainability**: {project_data.get('decision_explainability', 'Not provided')}
- **Output Documentation**: {project_data.get('output_documentation', 'Not provided')}""")
    
    # Accountability & Governance
    if any(project_data.get(f) for f in ['system_ownership', 'escalation_paths']):
        sections.append(f"""## Accountability & Governance
- **System Ownership**: {project_data.get('system_ownership', 'Not provided')}
- **Escalation Paths**: {project_data.get('escalation_paths', 'Not provided')}""")
    
    # Security & Privacy
    if any(project_data.get(f) for f in ['data_security', 'privacy_compliance']):
        sections.append(f"""## Security & Privacy
- **Data Security**: {project_data.get('data_security', 'Not provided')}
- **Privacy Compliance**: {project_data.get('privacy_compliance', 'Not provided')}""")
    
    # Impact & Risk
    if any(project_data.get(f) for f in ['potential_risks', 'risk_monitoring']):
        sections.append(f"""## Impact & Risk
- **Potential Risks**: {project_data.get('potential_risks', 'Not provided')}
- **Risk Monitoring & Mitigation**: {project_data.get('risk_monitoring', 'Not provided')}""")
    
    # User Interaction
    if any(project_data.get(f) for f in ['user_interaction_method', 'human_in_loop']):
        sections.append(f"""## User Interaction
- **Interaction Method**: {project_data.get('user_interaction_method', 'Not specified')}
- **Human-in-the-Loop**: {project_data.get('human_in_loop', 'Not specified')}""")
    
    full_prompt = f"""# Comprehensive Responsible AI Review Request

This is a DETAILED review submission with comprehensive information provided across all RAI dimensions. Please provide thorough, specific recommendations based on the detailed information provided.

{''.join(sections)}

---

Based on this comprehensive information, please provide:
1. An overall assessment considering ALL the information provided
2. Specific recommendations that address gaps identified in each section
3. Prioritized action items based on the deployment stage and risks identified
4. Recommended Microsoft tools with official documentation links

Focus on actionable, specific recommendations rather than generic advice since detailed context has been provided."""

    return full_prompt

def generate_recommendations_static(project_data):
    """Static recommendations as fallback when OpenAI is not available."""
    project_name = project_data.get("project_name", "Unknown Project")
    deployment_stage = project_data.get("deployment_stage", "Development")
    project_description = project_data.get("project_description", "")
    
    # Detect if this is an LLM/GenAI project
    is_llm_project = any(keyword in project_description.lower() for keyword in 
        ["llm", "gpt", "chatbot", "generative", "language model", "openai", "copilot", "assistant"])
    
    recommendations = []
    
    # Fairness recommendations
    fairness_rec = {
        "principle": MICROSOFT_RAI_PRINCIPLES["fairness"]["title"],
        "priority": "High",
        "description": MICROSOFT_RAI_PRINCIPLES["fairness"]["description"],
        "key_questions": MICROSOFT_RAI_PRINCIPLES["fairness"]["key_questions"],
        "recommendations": MICROSOFT_RAI_PRINCIPLES["fairness"]["best_practices"],
        "tools": MICROSOFT_RAI_TOOLS["fairness"]
    }
    recommendations.append(fairness_rec)
    
    # Reliability & Safety recommendations
    safety_rec = {
        "principle": MICROSOFT_RAI_PRINCIPLES["reliability_safety"]["title"],
        "priority": "Critical",
        "description": MICROSOFT_RAI_PRINCIPLES["reliability_safety"]["description"],
        "key_questions": MICROSOFT_RAI_PRINCIPLES["reliability_safety"]["key_questions"],
        "recommendations": MICROSOFT_RAI_PRINCIPLES["reliability_safety"]["best_practices"],
        "tools": MICROSOFT_RAI_TOOLS["safety"]
    }
    recommendations.append(safety_rec)
    
    # Privacy & Security recommendations
    privacy_rec = {
        "principle": MICROSOFT_RAI_PRINCIPLES["privacy_security"]["title"],
        "priority": "High",
        "description": MICROSOFT_RAI_PRINCIPLES["privacy_security"]["description"],
        "key_questions": MICROSOFT_RAI_PRINCIPLES["privacy_security"]["key_questions"],
        "recommendations": MICROSOFT_RAI_PRINCIPLES["privacy_security"]["best_practices"],
        "tools": MICROSOFT_RAI_TOOLS["privacy"] + MICROSOFT_RAI_TOOLS["security"]
    }
    recommendations.append(privacy_rec)
    
    # Inclusiveness recommendations
    inclusiveness_rec = {
        "principle": MICROSOFT_RAI_PRINCIPLES["inclusiveness"]["title"],
        "priority": "Medium",
        "description": MICROSOFT_RAI_PRINCIPLES["inclusiveness"]["description"],
        "key_questions": MICROSOFT_RAI_PRINCIPLES["inclusiveness"]["key_questions"],
        "recommendations": MICROSOFT_RAI_PRINCIPLES["inclusiveness"]["best_practices"],
        "tools": []  # Inclusiveness is more about process than tools
    }
    recommendations.append(inclusiveness_rec)
    
    # Transparency recommendations
    transparency_rec = {
        "principle": MICROSOFT_RAI_PRINCIPLES["transparency"]["title"],
        "priority": "High",
        "description": MICROSOFT_RAI_PRINCIPLES["transparency"]["description"],
        "key_questions": MICROSOFT_RAI_PRINCIPLES["transparency"]["key_questions"],
        "recommendations": MICROSOFT_RAI_PRINCIPLES["transparency"]["best_practices"],
        "tools": MICROSOFT_RAI_TOOLS["transparency"]
    }
    recommendations.append(transparency_rec)
    
    # Accountability recommendations
    accountability_rec = {
        "principle": MICROSOFT_RAI_PRINCIPLES["accountability"]["title"],
        "priority": "Medium",
        "description": MICROSOFT_RAI_PRINCIPLES["accountability"]["description"],
        "key_questions": MICROSOFT_RAI_PRINCIPLES["accountability"]["key_questions"],
        "recommendations": MICROSOFT_RAI_PRINCIPLES["accountability"]["best_practices"],
        "tools": MICROSOFT_RAI_TOOLS["accountability"]
    }
    recommendations.append(accountability_rec)
    
    # Add LLM-specific recommendations if applicable
    if is_llm_project:
        llm_rec = {
            "principle": "LLM/Generative AI Specific",
            "priority": "Critical",
            "description": "Additional considerations for Large Language Models and Generative AI systems.",
            "key_questions": [
                "How will you prevent prompt injection attacks?",
                "What content filters are in place for inputs and outputs?",
                "How will you detect and handle hallucinations?",
                "What guardrails prevent harmful content generation?"
            ],
            "recommendations": [
                "Implement Azure AI Content Safety for content moderation",
                "Use Prompt Shields to detect jailbreak attempts",
                "Enable Groundedness Detection to catch hallucinations",
                "Configure appropriate content filtering levels in Azure OpenAI",
                "Implement rate limiting and abuse detection",
                "Use system messages to establish clear AI behavior boundaries",
                "Log and monitor all LLM interactions for quality assurance"
            ],
            "tools": MICROSOFT_RAI_TOOLS["llm_specific"]
        }
        recommendations.insert(1, llm_rec)  # Add after fairness but before others
    
    # Add stage-specific recommendations
    if deployment_stage == "Production":
        production_rec = {
            "principle": "Production Readiness",
            "priority": "Critical",
            "description": "Critical checks before deploying AI systems to production.",
            "key_questions": [
                "Has the system passed all safety evaluations?",
                "Is monitoring and alerting configured?",
                "Are rollback procedures documented and tested?",
                "Have stakeholders signed off on deployment?"
            ],
            "recommendations": [
                "Complete pre-deployment checklist and sign-off",
                "Configure production monitoring with Azure Monitor and Application Insights",
                "Document and test rollback procedures",
                "Establish on-call rotation for incident response",
                "Set up automated alerts for safety and performance metrics",
                "Conduct final security review and penetration testing"
            ],
            "tools": [
                {
                    "name": "Azure Monitor",
                    "url": "https://azure.microsoft.com/products/monitor/",
                    "description": "Full-stack monitoring for applications and infrastructure.",
                    "category": "Monitoring"
                },
                {
                    "name": "Application Insights",
                    "url": "https://learn.microsoft.com/azure/azure-monitor/app/app-insights-overview",
                    "description": "Application performance management and monitoring.",
                    "category": "APM"
                }
            ]
        }
        recommendations.append(production_rec)
    elif deployment_stage == "Planning":
        planning_rec = {
            "principle": "Planning Phase",
            "priority": "High",
            "description": "Key considerations during the AI system planning phase.",
            "key_questions": [
                "Is AI the right solution for this problem?",
                "What are the potential harms and benefits?",
                "Who are the stakeholders and affected parties?",
                "What success metrics will be used?"
            ],
            "recommendations": [
                "Conduct a Responsible AI Impact Assessment",
                "Identify and engage key stakeholders early",
                "Define clear success metrics including fairness criteria",
                "Consider alternative non-AI solutions",
                "Document intended use cases and out-of-scope uses",
                "Establish governance and review processes"
            ],
            "tools": [
                {
                    "name": "Microsoft HAX Toolkit",
                    "url": "https://www.microsoft.com/haxtoolkit/",
                    "description": "Human-AI Experience guidelines and design patterns.",
                    "category": "Design"
                },
                {
                    "name": "AI Fairness Checklist",
                    "url": "https://www.microsoft.com/research/project/ai-fairness-checklist/",
                    "description": "Checklist for addressing fairness in AI systems.",
                    "category": "Assessment"
                }
            ]
        }
        recommendations.insert(0, planning_rec)
    
    return recommendations

@app.route("/api/health", methods=["GET"])
def health():
    azure_openai_configured = client is not None
    return jsonify({
        "status": "healthy", 
        "message": "Responsible AI Agent API", 
        "version": "4.0",  # Updated for adaptive system
        "features": {
            "adaptive_recommendations": ADAPTIVE_SYSTEM_AVAILABLE,
            "knowledge_base": KNOWLEDGE_AVAILABLE,
            "azure_openai": azure_openai_configured
        },
        "azure_openai": {
            "enabled": azure_openai_configured,
            "auth_method": auth_method if azure_openai_configured else None,
            "endpoint": AZURE_OPENAI_ENDPOINT if azure_openai_configured else None,
            "deployment": AZURE_OPENAI_DEPLOYMENT if azure_openai_configured else None
        }
    })


@app.route("/api/test-risk-assessment", methods=["POST"])
def test_risk_assessment():
    """
    TEST ENDPOINT: Returns mock data with enhanced risk assessment for UI testing.
    Remove this in production.
    """
    data = request.json or {}
    project_name = data.get("project_name", "Test Project")
    
    mock_response = {
        "submission_id": str(uuid.uuid4()),
        "project_name": project_name,
        "status": "completed",
        "ai_powered": True,
        "review_mode": "standard",
        "overall_assessment": {
            "summary": "This AI project shows moderate risk levels with key concerns around data privacy and content safety. The project benefits from being in the planning stage, allowing time for proper RAI implementation.",
            "maturity_level": "Developing",
            "key_strengths": ["Early-stage planning allows for proactive RAI integration", "Clear use case definition"],
            "critical_gaps": ["No content safety implementation", "Missing PII detection", "No bias testing planned"]
        },
        "risk_scores": {
            "overall_score": 58,
            "risk_level": "Moderate",
            "risk_summary": "This project presents moderate risk due to its customer-facing LLM chatbot handling potentially sensitive customer inquiries. The main concerns are lack of content safety controls, potential for harmful outputs, and absence of PII detection. However, being in the planning stage provides opportunity to implement proper safeguards before deployment.",
            "critical_factors": {
                "score_drivers_negative": [
                    {"factor": "Customer-facing LLM without content safety", "impact": "Users could be exposed to harmful, inappropriate, or factually incorrect responses", "severity": "High"},
                    {"factor": "Processing customer inquiries may include PII", "impact": "Personal data could be logged, stored insecurely, or exposed in responses", "severity": "High"},
                    {"factor": "No bias testing planned", "impact": "Chatbot may provide inconsistent or discriminatory responses to different user groups", "severity": "Medium"},
                    {"factor": "No human oversight mechanism", "impact": "Harmful patterns may go undetected until customer complaints arise", "severity": "Medium"}
                ],
                "score_drivers_positive": [
                    {"factor": "Project is in planning stage", "impact": "Allows time to implement proper safeguards before any deployment risk"},
                    {"factor": "Clear intended purpose defined", "impact": "Enables targeted risk assessment and appropriate tool selection"},
                    {"factor": "Not processing health or financial data", "impact": "Reduces regulatory complexity and compliance burden"}
                ]
            },
            "qualitative_assessment": {
                "data_sensitivity": {"level": "Medium", "rationale": "Customer inquiries may contain names, contact info, or preferences"},
                "user_impact": {"level": "High", "rationale": "Customer-facing system directly affects user experience and trust"},
                "regulatory_exposure": {"level": "Medium", "rationale": "May need to comply with GDPR, EU AI Act transparency requirements"},
                "technical_complexity": {"level": "Medium", "rationale": "LLM integration requires content safety, grounding, and monitoring"},
                "deployment_readiness": {"level": "Low", "rationale": "Significant gaps must be addressed before production deployment"}
            },
            "principle_scores": {
                "fairness": 55,
                "reliability_safety": 45,
                "privacy_security": 50,
                "inclusiveness": 65,
                "transparency": 60,
                "accountability": 55
            },
            "score_explanation": "Score reflects moderate risk from customer-facing LLM without proper content safety and privacy controls."
        },
        "recommendations_by_pillar": {
            "reliability_safety": {
                "pillar_name": "Reliability & Safety",
                "pillar_icon": "🛡️",
                "why_it_matters": "Your customer-facing chatbot will directly interact with users. Without safety controls, it could generate harmful, offensive, or factually incorrect responses that damage your brand and erode customer trust.",
                "risk_if_ignored": "Users could receive harmful content, leading to brand damage, customer complaints, potential legal action, and regulatory fines under EU AI Act.",
                "recommendations": [
                    {
                        "title": "Implement Azure AI Content Safety",
                        "why_needed": "Your chatbot will generate responses to customer inquiries. Content Safety is essential to prevent harmful outputs including hate speech, violence, self-harm content, and sexual content that could reach your customers.",
                        "what_happens_without": "Customers could receive inappropriate or harmful responses, leading to complaints, social media backlash, and potential regulatory violations under EU AI Act Article 52.",
                        "priority": "🚫 CRITICAL_BLOCKER",
                        "tool": {
                            "name": "Azure AI Content Safety",
                            "url": "https://learn.microsoft.com/azure/ai-services/content-safety/",
                            "how_it_helps": "Automatically scans inputs and outputs for harmful content across 4 categories (hate, violence, self-harm, sexual) with configurable severity thresholds."
                        },
                        "implementation_steps": ["Create Content Safety resource in Azure Portal", "Integrate SDK into your chatbot pipeline", "Configure severity thresholds based on your audience"]
                    }
                ]
            },
            "privacy_security": {
                "pillar_name": "Privacy & Security",
                "pillar_icon": "🔒",
                "why_it_matters": "Customer inquiries often contain personal information like names, emails, or account details. Without proper handling, this PII could be exposed in logs, responses, or model training.",
                "risk_if_ignored": "PII exposure could lead to GDPR violations (fines up to 4% of global revenue), customer data breaches, and loss of trust.",
                "recommendations": [
                    {
                        "title": "Implement PII Detection with Presidio",
                        "why_needed": "Customer messages may contain names, emails, phone numbers, or account numbers. You need to detect and handle this PII before processing or logging.",
                        "what_happens_without": "Customer PII could be stored in logs, used in model training, or exposed in responses to other users, violating GDPR and customer trust.",
                        "priority": "⚠️ HIGHLY_RECOMMENDED",
                        "tool": {
                            "name": "Microsoft Presidio",
                            "url": "https://microsoft.github.io/presidio/",
                            "how_it_helps": "Detects 50+ PII types across multiple languages and can anonymize or redact sensitive data before processing."
                        },
                        "implementation_steps": ["Install Presidio analyzer and anonymizer", "Configure entity recognizers for your use case", "Add to input preprocessing pipeline"]
                    }
                ]
            }
        },
        "next_steps": [
            "Set up Azure AI Content Safety resource and integrate into chatbot pipeline",
            "Implement Presidio for PII detection before logging or processing",
            "Design human escalation path for edge cases"
        ]
    }
    
    return jsonify(mock_response)


@app.route("/api/assess-input", methods=["POST"])
def assess_input():
    """
    NEW: Assess input completeness and return expected response depth.
    
    This helps the frontend show users what level of analysis they'll receive
    and what additional fields would improve their review.
    """
    try:
        project_data = request.get_json() or {}
        
        if ADAPTIVE_SYSTEM_AVAILABLE:
            from response_adapter import InputAssessor
            
            # Assess input
            assessment = InputAssessor.assess_input(project_data)
            project_characteristics = InputAssessor.detect_project_type(project_data)
            
            return jsonify({
                "completeness_score": assessment["completeness_score"],
                "response_depth": assessment["response_depth"].value,
                "review_mode": {
                    "minimal": "quick_guidance",
                    "basic": "quick_scan", 
                    "standard": "standard_review",
                    "comprehensive": "deep_dive"
                }.get(assessment["response_depth"].value, "quick_guidance"),
                "provided_fields": assessment["provided_fields"],
                "field_count": assessment["field_count"],
                "total_fields": assessment["total_fields"],
                "suggestions_for_better_review": assessment["suggestions"],
                "detected_project_type": project_characteristics.get("primary_type", "General AI"),
                "project_characteristics": {
                    "is_llm_project": project_characteristics.get("is_llm_project", False),
                    "is_agent_project": project_characteristics.get("is_agent_project", False),
                    "is_high_risk": project_characteristics.get("is_high_risk", False),
                    "handles_pii": project_characteristics.get("handles_pii", False),
                    "is_customer_facing": project_characteristics.get("is_customer_facing", False)
                },
                "depth_descriptions": {
                    "minimal": "Quick guidance with essential tools and getting started steps",
                    "basic": "Quick scan with reference architectures and 30-day roadmap",
                    "standard": "Full analysis across all RAI principles with detailed recommendations",
                    "comprehensive": "Deep dive with custom implementation roadmap and exhaustive analysis"
                }
            })
        else:
            # Fallback - basic assessment without adaptive system
            provided = [k for k, v in project_data.items() if v and str(v).strip()]
            return jsonify({
                "completeness_score": min(100, len(provided) * 10),
                "response_depth": "standard",
                "review_mode": "standard_review",
                "field_count": len(provided),
                "suggestions_for_better_review": [],
                "adaptive_system_available": False
            })
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/priority-levels", methods=["GET"])
def get_priority_levels():
    """
    NEW: Return the priority level definitions for frontend display.
    """
    return jsonify({
        "priority_levels": [
            {
                "level": "CRITICAL_BLOCKER",
                "display_name": "Critical Blocker",
                "icon": "🚫",
                "color": "#dc2626",
                "description": "Must be addressed before production deployment. Non-negotiable for responsible AI.",
                "action_required": True
            },
            {
                "level": "HIGHLY_RECOMMENDED",
                "display_name": "Highly Recommended",
                "icon": "⚠️",
                "color": "#f59e0b",
                "description": "Strongly recommended for production readiness. Significant risk if not addressed.",
                "action_required": True
            },
            {
                "level": "RECOMMENDED",
                "display_name": "Recommended",
                "icon": "✅",
                "color": "#10b981",
                "description": "Best practice that improves RAI posture. Should be part of the roadmap.",
                "action_required": False
            },
            {
                "level": "NICE_TO_HAVE",
                "display_name": "Nice to Have",
                "icon": "💡",
                "color": "#6366f1",
                "description": "Enhancement that optimizes the system. Can be prioritized based on resources.",
                "action_required": False
            }
        ]
    })

@app.route("/api/submit-review", methods=["POST"])
def submit_review():
    try:
        project_data = request.get_json() or {}
        
        # Use adaptive AI-powered recommendations if available
        if client:
            ai_response = generate_recommendations_adaptive(project_data)
            
            # If we got a proper AI response, use it
            # Check for both old format (recommendations) and new format (recommendations_by_pillar)
            has_recommendations = (
                "recommendations" in ai_response or 
                "recommendations_by_pillar" in ai_response
            )
            if has_recommendations and not ai_response.get("fallback"):
                # Augment response with dynamic reference architectures if missing
                ai_response = augment_with_dynamic_resources(ai_response, project_data)
                
                return jsonify({
                    "submission_id": str(uuid.uuid4()),
                    "project_name": project_data.get("project_name", "Unknown"),
                    "ai_powered": True,
                    **ai_response
                })
        
        # Fallback to static recommendations
        recommendations = generate_recommendations_static(project_data)
        
        response_data = {
            "submission_id": str(uuid.uuid4()),
            "project_name": project_data.get("project_name", "Unknown"),
            "recommendations": recommendations,
            "status": "completed",
            "summary": {
                "total_recommendations": len(recommendations),
                "critical_items": sum(1 for r in recommendations if r["priority"] == "Critical"),
                "high_priority_items": sum(1 for r in recommendations if r["priority"] == "High")
            },
            "microsoft_rai_resources": {
                "overview": "https://www.microsoft.com/ai/responsible-ai",
                "standards": "https://learn.microsoft.com/azure/machine-learning/concept-responsible-ai",
                "tools": "https://www.microsoft.com/ai/tools-practices"
            }
        }

        # Populate risk scores and pillar grouping for the static fallback path
        response_data["risk_scores"] = calculate_basic_risk_scores(project_data)
        response_data["recommendations_by_pillar"] = build_static_pillar_recommendations(recommendations)

        return jsonify(response_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/submit-advanced-review", methods=["POST"])
def submit_advanced_review():
    """Handle comprehensive/advanced review submissions with detailed questionnaire data."""
    try:
        project_data = request.get_json() or {}
        
        # Use adaptive AI-powered recommendations (handles all input levels)
        if client:
            ai_response = generate_recommendations_adaptive(project_data)
            
            # If we got a proper AI response, use it
            # Check for both old format (recommendations) and new format (recommendations_by_pillar)
            has_recommendations = (
                "recommendations" in ai_response or 
                "recommendations_by_pillar" in ai_response
            )
            if has_recommendations and not ai_response.get("fallback"):
                # Augment response with dynamic reference architectures if missing
                ai_response = augment_with_dynamic_resources(ai_response, project_data)
                
                return jsonify({
                    "submission_id": str(uuid.uuid4()),
                    "project_name": project_data.get("project_name", "Unknown"),
                    "ai_powered": True,
                    "review_type": "comprehensive",
                    **ai_response
                })
        
        # Fallback to static recommendations
        recommendations = generate_recommendations_static(project_data)
        
        response_data = {
            "submission_id": str(uuid.uuid4()),
            "project_name": project_data.get("project_name", "Unknown"),
            "review_type": "comprehensive",
            "recommendations": recommendations,
            "status": "completed",
            "summary": {
                "total_recommendations": len(recommendations),
                "critical_items": sum(1 for r in recommendations if r["priority"] == "Critical"),
                "high_priority_items": sum(1 for r in recommendations if r["priority"] == "High")
            },
            "microsoft_rai_resources": {
                "overview": "https://www.microsoft.com/ai/responsible-ai",
                "standards": "https://learn.microsoft.com/azure/machine-learning/concept-responsible-ai",
                "tools": "https://www.microsoft.com/ai/tools-practices"
            }
        }
        
        response_data["risk_scores"] = calculate_basic_risk_scores(project_data)
        response_data["recommendations_by_pillar"] = build_static_pillar_recommendations(recommendations)

        return jsonify(response_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/tools", methods=["GET"])
def get_tools():
    """Return all available Microsoft RAI tools organized by category."""
    # Use knowledge loader if available for dynamic tools
    if KNOWLEDGE_AVAILABLE and knowledge_loader:
        try:
            catalog = knowledge_loader.tools_catalog
            if catalog:
                return jsonify({
                    "tools": catalog.get("categories", {}),
                    "quick_reference": catalog.get("quick_reference", {}),
                    "client_framework": catalog.get("client_recommendation_framework", {}),
                    "use_cases": catalog.get("actionable_use_cases", {}),
                    "metadata": catalog.get("catalog_metadata", {}),
                    "source": "knowledge_base"
                })
        except Exception as e:
            print(f"Error loading from knowledge base: {e}")
    
    # Fallback to static tools
    return jsonify({
        "tools": MICROSOFT_RAI_TOOLS,
        "principles": {k: {"title": v["title"], "description": v["description"]} 
                      for k, v in MICROSOFT_RAI_PRINCIPLES.items()},
        "source": "static"
    })


@app.route("/api/references", methods=["GET"])
def get_references():
    """Return Microsoft RAI documentation references and resources."""
    if KNOWLEDGE_AVAILABLE and knowledge_loader:
        try:
            refs = knowledge_loader.microsoft_references
            if refs:
                return jsonify({
                    "references": refs,
                    "source": "knowledge_base"
                })
        except Exception as e:
            print(f"Error loading references from knowledge base: {e}")
    
    # Fallback - no references available
    return jsonify({
        "references": {},
        "source": "static",
        "message": "No references available"
    })


@app.route("/api/reference-architectures", methods=["GET"])
def get_reference_architectures():
    """
    Return dynamic reference architectures and starter templates.
    
    Query params:
    - project_type: chatbot, multi_agent, document_processing, etc.
    - use_case: specific use case for filtering
    - refresh: force refresh of cached data
    """
    project_type = request.args.get("project_type", "chatbot")
    use_case = request.args.get("use_case", "")
    force_refresh = request.args.get("refresh", "false").lower() == "true"
    
    # Try dynamic resources first
    if DYNAMIC_RESOURCES_AVAILABLE:
        try:
            fetcher = get_dynamic_fetcher()
            
            # Pass OpenAI client for Bing grounding if available
            if client:
                fetcher.openai_client = client
                fetcher.openai_deployment = AZURE_OPENAI_DEPLOYMENT
            
            if force_refresh:
                fetcher.clear_cache("reference_architectures")
                fetcher.clear_cache("github_repos")
            
            architectures = fetcher.get_reference_architectures(project_type, use_case)
            
            return jsonify({
                "architectures": architectures,
                "project_type": project_type,
                "cache_stats": fetcher.get_cache_stats(),
                "source": "dynamic"
            })
        except Exception as e:
            print(f"Dynamic resources error: {e}")
    
    # Fallback to static knowledge base
    if KNOWLEDGE_AVAILABLE and knowledge_loader:
        try:
            arch_file = knowledge_loader._load_json("reference_architectures.json")
            if arch_file:
                patterns = arch_file.get("architecture_patterns", {})
                # Filter by project type if matching
                relevant = {}
                for key, pattern in patterns.items():
                    if project_type.lower() in key.lower() or not project_type:
                        relevant[key] = pattern
                
                return jsonify({
                    "architectures": relevant if relevant else patterns,
                    "project_type": project_type,
                    "learning_paths": arch_file.get("learning_paths", []),
                    "rai_tools": arch_file.get("responsible_ai_tools", {}),
                    "source": "knowledge_base"
                })
        except Exception as e:
            print(f"Knowledge base fallback error: {e}")
    
    # Final fallback - minimal response
    return jsonify({
        "architectures": {},
        "project_type": project_type,
        "source": "none",
        "message": "Reference architectures not available. Please check backend configuration."
    })


@app.route("/api/github-repos", methods=["GET"])
def get_github_repos():
    """
    Return live GitHub repository information for Azure AI samples.
    
    Query params:
    - limit: number of repos to return (default 10)
    - refresh: force refresh of cached data
    """
    limit = request.args.get("limit", 10, type=int)
    force_refresh = request.args.get("refresh", "false").lower() == "true"
    
    if DYNAMIC_RESOURCES_AVAILABLE:
        try:
            fetcher = get_dynamic_fetcher()
            
            if force_refresh:
                fetcher.clear_cache("github_repos")
            
            repos = fetcher.get_popular_azure_samples(limit)
            
            return jsonify({
                "repos": repos,
                "count": len(repos),
                "cache_stats": fetcher.get_cache_stats(),
                "source": "github_api"
            })
        except Exception as e:
            print(f"GitHub repos error: {e}")
    
    # Fallback to static list from knowledge base
    if KNOWLEDGE_AVAILABLE and knowledge_loader:
        try:
            arch_file = knowledge_loader._load_json("reference_architectures.json")
            if arch_file:
                all_repos = []
                for pattern in arch_file.get("architecture_patterns", {}).values():
                    for template in pattern.get("github_templates", []):
                        all_repos.append({
                            "repo": template.get("repo", ""),
                            "description": template.get("description", ""),
                            "language": template.get("language", ""),
                            "stars": template.get("stars_approx", 0),
                            "deployment_command": template.get("deployment_command", "")
                        })
                
                return jsonify({
                    "repos": all_repos[:limit],
                    "count": len(all_repos[:limit]),
                    "source": "knowledge_base_static"
                })
        except Exception as e:
            print(f"Knowledge base repos fallback error: {e}")
    
    return jsonify({
        "repos": [],
        "count": 0,
        "source": "none",
        "message": "GitHub repository information not available"
    })


@app.route("/api/knowledge/status", methods=["GET"])
def knowledge_status():
    """Get the status of the knowledge base files."""
    if not KNOWLEDGE_AVAILABLE or not knowledge_loader:
        return jsonify({
            "available": False,
            "message": "Knowledge loader not initialized"
        })
    
    try:
        status = knowledge_loader.get_knowledge_status()
        return jsonify({
            "available": True,
            **status
        })
    except Exception as e:
        return jsonify({
            "available": False,
            "error": str(e)
        }), 500


@app.route("/api/knowledge/reload", methods=["POST"])
def reload_knowledge():
    """Reload all knowledge files from disk (hot reload)."""
    if not KNOWLEDGE_AVAILABLE or not knowledge_loader:
        return jsonify({
            "success": False,
            "message": "Knowledge loader not initialized"
        }), 400
    
    try:
        knowledge_loader.reload_all()
        # Force reload by accessing properties
        _ = knowledge_loader.tools_catalog
        _ = knowledge_loader.microsoft_references
        _ = knowledge_loader.regulatory_frameworks
        _ = knowledge_loader.code_examples
        
        status = knowledge_loader.get_knowledge_status()
        return jsonify({
            "success": True,
            "message": "Knowledge base reloaded successfully",
            **status
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/knowledge/recommendations", methods=["POST"])
def get_tailored_recommendations():
    """Get tailored tool recommendations based on client context."""
    if not KNOWLEDGE_AVAILABLE or not knowledge_loader:
        return jsonify({
            "error": "Knowledge loader not initialized"
        }), 400
    
    try:
        data = request.get_json() or {}
        industry = data.get("industry")
        use_case = data.get("use_case")
        
        recommendations = {}
        
        if industry:
            ind_rec = knowledge_loader.get_industry_recommendation(industry)
            if ind_rec:
                recommendations["industry"] = ind_rec
        
        if use_case:
            uc_rec = knowledge_loader.get_use_case_recommendation(use_case)
            if uc_rec:
                recommendations["use_case"] = uc_rec
        
        # Add implementation phases
        recommendations["implementation_phases"] = knowledge_loader.get_implementation_phases()
        
        return jsonify({
            "success": True,
            "recommendations": recommendations
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
